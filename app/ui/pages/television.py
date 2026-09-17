from datetime import datetime
from pathlib import Path

from nicegui import ui

from app.config.channel_catalog import CATALOG_BY_SHORT_NAME
from app.services.channel_group_service import ChannelGroupService
from app.services.channel_service import ChannelService
from app.services.program_service import ProgramService


STYLE_PATH = Path(__file__).resolve().parents[1] / 'styles.css'


def register_television_page(
    channel_service: ChannelService,
    channel_group_service: ChannelGroupService,
    program_service: ProgramService,
) -> None:
    @ui.page('/')
    def television_page() -> None:
        ui.add_css(STYLE_PATH.read_text(encoding='utf-8'))
        container = ui.column().classes('tv-shell gap-0')
        expanded_program_ids: set[int] = set()

        def channel_options() -> dict[int, str]:
            return {
                channel.id: f'{channel.short_name} · {channel.name}'
                for channel in channel_service.list_enabled()
                if channel.id is not None
            }

        def open_group_dialog(group_id: int | None = None, group_name: str = '') -> None:
            selected = channel_group_service.member_ids(group_id) if group_id else []
            with ui.dialog() as dialog, ui.card().classes('tv-dialog'):
                ui.label('Tabelle bearbeiten' if group_id else 'Neue Tabelle').classes('tv-dialog-title')
                name_input = ui.input('Name', value='Neue Sendergruppe' if group_id is None else group_name).classes('w-full')
                if group_id is not None:
                    name_input.disable()
                selection = ui.select(channel_options(), value=selected, multiple=True, label='Sender').classes('w-full')
                with ui.row().classes('justify-end w-full'):
                    ui.button('Abbrechen', on_click=dialog.close).props('flat')

                    def save() -> None:
                        channel_ids = [int(channel_id) for channel_id in selection.value or []]
                        if group_id is None:
                            channel_group_service.create(name_input.value.strip() or 'Neue Sendergruppe', channel_ids)
                        else:
                            channel_group_service.replace_members(group_id, channel_ids)
                        dialog.close()
                        render()

                    ui.button('Speichern', on_click=save)
            dialog.open()

        def render() -> None:
            container.clear()
            now = datetime.now()
            all_channels = channel_service.list_enabled()
            program_service.refresh(all_channels, now)
            overview_by_channel_id = {
                overview.channel.id: overview
                for overview in program_service.build_overviews(all_channels, now)
            }

            with container:
                with ui.row().classes('tv-header items-end no-wrap'):
                    with ui.column().classes('gap-0'):
                        ui.label('Television').classes('tv-title')
                        ui.label('Aktuelles Fernsehprogramm').classes('tv-subtitle')
                    ui.button('+ Tabelle', on_click=open_group_dialog).classes('tv-add-group').props('outline')

                for group, channels in channel_group_service.list_groups_with_channels():
                    with ui.element('section').classes('tv-group'):
                        with ui.row().classes('tv-group-header items-center no-wrap'):
                            ui.label(group.name).classes('tv-group-title')
                            ui.space()
                            ui.button(icon='tune', on_click=lambda group_id=group.id, group_name=group.name: open_group_dialog(group_id, group_name)).props('flat round dense').tooltip('Sender auswählen')

                        with ui.element('div').classes('tv-table'):
                            for channel in channels:
                                overview = overview_by_channel_id[channel.id]
                                catalog_channel = CATALOG_BY_SHORT_NAME[channel.short_name]
                                current = overview.current_program

                                with ui.element('div').classes('tv-row'):
                                    with ui.link(target=catalog_channel.stream_url, new_tab=True).classes('tv-channel-link'):
                                        ui.image(catalog_channel.logo_url).classes('tv-channel-logo')
                                        ui.label(channel.short_name).classes('tv-channel')

                                    ui.label(f'{current.start_at:%H:%M}–{current.end_at:%H:%M}' if current else '—').classes('tv-time')

                                    with ui.element('div').classes('tv-program').on(
                                        'click',
                                        lambda program_id=current.id if current else None: toggle_program(program_id),
                                    ):
                                        ui.label(current.title if current else 'Kein aktuelles Programm').classes('tv-program-title')
                                        if current and current.subtitle:
                                            ui.label(current.subtitle).classes('tv-subtitle-program')
                                        if current and current.id in expanded_program_ids and current.description:
                                            ui.label(current.description).classes('tv-description')
                                        if current:
                                            duration = (current.end_at - current.start_at).total_seconds()
                                            elapsed = (now - current.start_at).total_seconds()
                                            progress = min(100, max(0, elapsed / duration * 100)) if duration else 0
                                            ui.element('div').classes('tv-progress').style(f'--progress: {progress:.1f}%')
                                        if overview.next_program:
                                            with ui.element('div').classes('tv-next'):
                                                ui.label(f'{overview.next_program.start_at:%H:%M}–{overview.next_program.end_at:%H:%M}').classes('tv-next-time')
                                                ui.label(overview.next_program.title)
                                        if overview.following_program:
                                            with ui.element('div').classes('tv-following'):
                                                ui.label(f'{overview.following_program.start_at:%H:%M}–{overview.following_program.end_at:%H:%M}').classes('tv-next-time')
                                                ui.label(overview.following_program.title)

                                    ui.label(current.category or '' if current else '').classes('tv-info')

                                    with ui.element('div').classes('tv-sort'):
                                        ui.button(icon='keyboard_arrow_up', on_click=lambda channel_id=channel.id: move(channel_id, -1)).props('flat round dense').tooltip('Sender nach oben')
                                        ui.button(icon='keyboard_arrow_down', on_click=lambda channel_id=channel.id: move(channel_id, 1)).props('flat round dense').tooltip('Sender nach unten')

        def move(channel_id: int | None, offset: int) -> None:
            if channel_id is None:
                return
            channel_service.move(channel_id, offset)
            render()

        def toggle_program(program_id: int | None) -> None:
            if program_id is None:
                return
            if program_id in expanded_program_ids:
                expanded_program_ids.remove(program_id)
            else:
                expanded_program_ids.add(program_id)
            render()

        render()

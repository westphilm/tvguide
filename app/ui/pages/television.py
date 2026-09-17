from datetime import datetime
from pathlib import Path

from nicegui import ui

from app.config.channel_catalog import CATALOG_BY_SHORT_NAME
from app.services.channel_group_service import ChannelGroupService
from app.services.channel_service import ChannelService
from app.services.program_service import ProgramService


STYLE_PATH = Path(__file__).resolve().parents[1] / 'styles.css'
WEEKDAYS = ('Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So')


def register_television_page(
    channel_service: ChannelService,
    channel_group_service: ChannelGroupService,
    program_service: ProgramService,
) -> None:
    @ui.page('/')
    def television_page() -> None:
        ui.add_css(STYLE_PATH.read_text(encoding='utf-8'))
        container = ui.column().classes('tv-shell gap-0')
        expanded_channel_ids: set[int] = set()
        dynamic_rows: dict[int, tuple[object, object]] = {}
        program_date_label = None

        def format_program_date(value: datetime) -> str:
            return f'Programm: {WEEKDAYS[value.weekday()]} {value:%d.%m.%Y}'

        def toggle_theme() -> None:
            ui.run_javascript('''
                const isLight = document.documentElement.classList.toggle('tv-light');
                localStorage.setItem('television-theme', isLight ? 'light' : 'dark');
            ''')

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
                selection = ui.select(channel_options(), value=selected, multiple=True, label='Sender').classes('w-full tv-channel-select').props('popup-content-class=tv-select-menu')
                with ui.row().classes('justify-end w-full'):
                    ui.button('Abbrechen', on_click=dialog.close).props('flat')

                    def save() -> None:
                        channel_ids = [int(channel_id) for channel_id in selection.value or []]
                        if group_id is None:
                            channel_group_service.create(name_input.value.strip() or 'Neue Sendergruppe', channel_ids)
                        else:
                            channel_group_service.rename(group_id, name_input.value.strip() or group_name)
                            channel_group_service.replace_members(group_id, channel_ids)
                        dialog.close()
                        render()

                    ui.button('Speichern', on_click=save)
            dialog.open()

        def render() -> None:
            nonlocal program_date_label
            container.clear()
            dynamic_rows.clear()
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
                        program_date_label = ui.label(format_program_date(now)).classes('tv-subtitle')
                    with ui.row().classes('tv-header-actions items-center no-wrap'):
                        ui.button('+ Tabelle', on_click=open_group_dialog).classes('tv-add-group').props('outline')
                        ui.button(icon='brightness_4', on_click=toggle_theme).classes('tv-theme-toggle').props('flat round dense').tooltip('Helles/dunkles Design wechseln')

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
                                    with ui.link(target=catalog_channel.homepage_url, new_tab=True).classes('tv-channel-link'):
                                        ui.image(catalog_channel.logo_url).classes('tv-channel-logo')
                                        ui.label(channel.short_name).classes('tv-channel')

                                    with ui.element('div').classes('tv-time'):
                                        time_start_label = ui.label().classes('tv-time-start')
                                        time_end_label = ui.label().classes('tv-time-end')

                                    with ui.element('div').classes('tv-program').on(
                                        'click',
                                        lambda channel_id=channel.id: toggle_program(channel_id),
                                    ):
                                        title_label = ui.label().classes('tv-program-title')
                                        subtitle_label = ui.label().classes('tv-subtitle-program')
                                        description_label = ui.label().classes('tv-description')
                                        progress_bar = ui.element('div').classes('tv-progress')
                                        with ui.element('div').classes('tv-next') as next_row:
                                            next_time_label = ui.label().classes('tv-next-time')
                                            next_title_label = ui.label()
                                        with ui.element('div').classes('tv-following') as following_row:
                                            following_time_label = ui.label().classes('tv-next-time')
                                            following_title_label = ui.label()

                                    info_label = ui.label().classes('tv-info')

                                    with ui.element('div').classes('tv-sort'):
                                        with ui.link(target=catalog_channel.stream_url, new_tab=True).classes('tv-media-link'):
                                            ui.button(icon='play_circle').props('flat round dense').tooltip('Zur Mediathek')
                                        ui.button(icon='keyboard_arrow_up', on_click=lambda channel_id=channel.id: move(channel_id, -1)).props('flat round dense').tooltip('Sender nach oben')
                                        ui.button(icon='keyboard_arrow_down', on_click=lambda channel_id=channel.id: move(channel_id, 1)).props('flat round dense').tooltip('Sender nach unten')

                                def update_row(
                                    updated_overview,
                                    timestamp,
                                    channel_id=channel.id,
                                    time_start_label=time_start_label,
                                    time_end_label=time_end_label,
                                    title_label=title_label,
                                    subtitle_label=subtitle_label,
                                    description_label=description_label,
                                    progress_bar=progress_bar,
                                    next_row=next_row,
                                    next_time_label=next_time_label,
                                    next_title_label=next_title_label,
                                    following_row=following_row,
                                    following_time_label=following_time_label,
                                    following_title_label=following_title_label,
                                    info_label=info_label,
                                ):
                                    updated_current = updated_overview.current_program
                                    time_start_label.set_text(f'{updated_current.start_at:%H:%M}' if updated_current else '—')
                                    time_end_label.set_text(f' - {updated_current.end_at:%H:%M}' if updated_current else '')
                                    title_label.set_text(updated_current.title if updated_current else 'Kein aktuelles Programm')
                                    subtitle_label.set_text(updated_current.subtitle or '' if updated_current else '')
                                    subtitle_label.set_visibility(bool(updated_current and updated_current.subtitle))
                                    description_label.set_text(updated_current.description or '' if updated_current else '')
                                    description_label.set_visibility(
                                        bool(updated_current and updated_current.description and channel_id in expanded_channel_ids)
                                    )
                                    info_label.set_text(updated_current.category or '' if updated_current else '')
                                    progress_bar.set_visibility(bool(updated_current))
                                    if updated_current:
                                        duration = (updated_current.end_at - updated_current.start_at).total_seconds()
                                        elapsed = (timestamp - updated_current.start_at).total_seconds()
                                        progress = min(100, max(0, elapsed / duration * 100)) if duration else 0
                                        progress_bar.style(f'--progress: {progress:.1f}%')

                                    next_program = updated_overview.next_program
                                    next_row.set_visibility(bool(next_program))
                                    next_time_label.set_text(
                                        f'{next_program.start_at:%H:%M} - {next_program.end_at:%H:%M}' if next_program else ''
                                    )
                                    next_title_label.set_text(next_program.title if next_program else '')
                                    following_program = updated_overview.following_program
                                    following_row.set_visibility(bool(following_program))
                                    following_time_label.set_text(
                                        f'{following_program.start_at:%H:%M} - {following_program.end_at:%H:%M}' if following_program else ''
                                    )
                                    following_title_label.set_text(following_program.title if following_program else '')

                                if channel.id is not None:
                                    dynamic_rows[channel.id] = (update_row, overview)
                                    update_row(overview, now)

        def move(channel_id: int | None, offset: int) -> None:
            if channel_id is None:
                return
            channel_service.move(channel_id, offset)
            render()

        def toggle_program(channel_id: int | None) -> None:
            if channel_id is None:
                return
            if channel_id in expanded_channel_ids:
                expanded_channel_ids.remove(channel_id)
            else:
                expanded_channel_ids.add(channel_id)
            updater, overview = dynamic_rows[channel_id]
            updater(overview, datetime.now())

        def refresh_dynamic_rows() -> None:
            now = datetime.now()
            if program_date_label is not None:
                program_date_label.set_text(format_program_date(now))
            all_channels = channel_service.list_enabled()
            program_service.refresh(all_channels, now)
            overviews = {
                overview.channel.id: overview
                for overview in program_service.build_overviews(all_channels, now)
            }
            for channel_id, (updater, _) in dynamic_rows.items():
                overview = overviews.get(channel_id)
                if overview:
                    dynamic_rows[channel_id] = (updater, overview)
                    updater(overview, now)

        render()
        ui.run_javascript('''
            if (localStorage.getItem('television-theme') === 'light') {
                document.documentElement.classList.add('tv-light');
            }
        ''')
        ui.timer(60.0, refresh_dynamic_rows)

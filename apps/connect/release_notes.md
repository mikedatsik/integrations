# ftrack Connect release Notes

## Upcoming
YYYY-mm-dd

* [changed] Do not prevent Connect from launching if there is no system tray.
* [changed] Support for detecting and warning about integrations requiring Rosetta on Apple Silicon. 
* [changed] Ported and integrated the ftrack-application-launcher module and switched over to YAML configuration support.
* [changed] Support for environment variables in launcher configs.
* [changed] Ported and integrated the ftrack-connect-action-launcher-widget.
* [changed] Made it read from Github releases instead of AWS plugin space.
* [changed] Ported and integrated the ftrack-connect-plugin-manager
* [new] Support for new extension based integrations, utilising the ftrack-utils library.


## v2.1.1
2023-04-27

* [fixed] Plugins. Limit packaging to prevent crashes on unexpected content in Connect plugin folder.

## v2.1.0
2023-04-05

* [changed] Plugins. Install all plugins on first launch.
* [changed] Docs. Update CONTRIBUTING.md to include release notes.
* [fixed] UI. Application crash on Windows 8.1.
* [fixed] API. Ensure all plugin paths are unique.

## v2.0.1
2022-09-01

* [fixed] UX. Action icons are being cut in task launcher.
* [fixed] UX. Icons fonts are not correctly loaded during storage setup.

## v2.0.0
2022-07-07

* [fixed] UX. User's tasks include inactive projects.
* [changed] Tray. Windows and Linux use color icon in system tray.
* [fixed] Style. Variant are highlighted black on light style.
* [fixed] Linux. Application shortcut points to wrong executable.
* [fixed] UX. Path with unicode are not rendered spaced correctly.

## v2.0.0-rc-6
2022-06-01

* [changed] Login. Provide link to get back on logging in through instance address.
* [changed] Style. Remove play button from action launch and review style.
* [fixed] UX. Interface expand on long context paths.
* [fixed] Publisher. Add missing icons and set correct state for drop zone on folders.
* [fixed] Publisher. Latest published assets are not always refreshing.
* [changed] Style. Review Dialogs styles.
* [changed] Style. Review style and icons.
* [new] SystemTray, API. Allow connect to restart.
* [changed] Plugins. Remove publisher and launcher from connect codebase. Documentation can be found in:
        Publisher documentation
        Launcher documentation
* [changed] Codestyle. Run black pass with flags : black --skip-string-normalization -l 79 . on Codebase.

## v2.0.0-rc-5
2022-03-25

* [fixed] Actions. Random crashes on discovering on null context.
* [new] Module. Provide ftrak_connect.qt module to abstract imported Qt modules.
* [changed] Events. Sending of usage_events can now be batched.
* [changed] About, Linux. Linux Desktop entry respect packaged or virtual environment paths.
* [changed] UX. Add new icons set for Connect.
* [changed] UX. Connect color theme respect system theme.

## v2.0.0-rc-4
2022-01-15

* [changed] UX. Assigned tasks are refreshed on cancel.
* [changed] API. User's plugin folder is created at startup time.
* [changed] UX. Context selection is changed to a list of assigned tasks.
* [new] UX. Indicator during discovery of actions.
* [new] API. Provide ConnectWidget Plugin with custom name attribute to render.
* [new] API. Improve ConnectWidget error logging.
* [new] API. Emit usage data for Connect session duration along version and os type.
* [fixed] API. Storage scenario help points to dead link.
* [changed] UX. Provide placeholder text in context selectors.
* [fixed] UX. Menubar icon smaller on Mac.
* [changed] UX. Update icon set to use font icons (material/ftrack icons) to ensure full hidpi support.
* [changed] UX. Consolidate font using Roboto.
* [changed] API. Remove ftrack_connect.session utility class, and shared_session usage.
* [changed] Logging. Improve logging readability.
* [new] API. Restore ftrack_connect.application module to provide environment variable helper methods.

## v2.0.0-rc-3
2021-09-23

* [changed] Setup. Use latest api release version.
* [fixed] API. Cannot publish after a failed publish, and need to restart connect.

## v2.0.0-rc-2
2021-07-13

* [changed] Documentation. Update with latest images.

## v2.0.0-rc-1
2021-06-18

* [changed] UI. Integrations are returned sorted by name in About page.
* [changed] ConnectWidgetPlugin. Improve error handling.

## v2.0.0-beta-4
2021-06-07

* [new] UI. Allow connect to be always on top of other windows.

## v2.0.0-beta-3
2021-05-21

* [changed] API. Review ConnectWidgetPlugin base classes.

## v2.0.0-beta-2
2021-03-18

* [new] Ui. Provide ability to extend connect through ConnectWidgets plugins.

## v2.0.0-beta-1
2021-03-11

* [changed] Ui. Move to Pyside2.
* [changed] API. Remove ftrack-python-legacy-api dependency and dependent code.
* [new] Ui. Replace QtExt with Qt.py module.
* [changed] Changed. Move connector integration codebase to separate repository.
* [new] Setup. Use setuptool_scm to infer version.
* [fixed] Application launcher. Standalone installation does not correctly inject dependencies at application startup.
* [changed] Code. Port code to python3.

## v1.1.10
2021-05-21

* [fixed] Doc. Provide requirement file for RTD builds.

## v1.1.9
2021-03-11

* [fixed] Open_directory. Opening component breaks on cloud paths.
* [fixed] Application launcher. Standalone installation does not correctly inject dependencies at application startup.

## v1.1.8
2020-01-21

* [new] Internal. Added a lockfile mechanism so Connect will exit if another instance is already running. Users can pass a command-line flag, -a or --allow-multiple, to skip this check.

## v1.1.7
2019-03-08

* [new] Ui. Added button in About dialog to create a Linux desktop entry file to make Connect appear in the applications menu.

## v1.1.6
2018-10-8

* [changed] Ui. Update icons and style.
* [fixed] Internal. Util.open_directory fails on Windows when path includes spaces.

## v1.1.5
2018-09-13

* [fixed] Logging. Logger breaks with non ascii path.
* [changed] Logging. Improve logging configuration.
* [fixed] Ui. Application versions are not correctly sorted.

## v1.1.4
2018-04-27

* [fixed] Import asset. Import Asset breaks checking for asset in remote locations.
* [changed] Crew. Remove Crew widget chat and notifications.
* [changed] Ui. Added feature to hide the ftrack-connect UI on startup. This is done with the flag "--silent" or "-s".

## v1.1.3
2018-02-02

* [fixed] Plugins. ftrack.connect.plugin.debug-information only published for the legacy api.

## v1.1.2
2017-12-01

* [fixed] Documentation. Release notes page is not formatted correct.

## v1.1.1
2017-11-16

* [fixed] API. Error when publishing in connect with non-task context.

## v1.1.0
2017-09-12

* [changed] Import asset. Component location picker now defaults to location where the component exists. If a component exists in more than one location, the priority order determines the default location.
* [fixed] Info dialog, Tasks dialog. Info and Tasks dialogs are not compatible with recent versions of Qt.
* [fixed] API. All widgets are not compatible with recent versions of Qt.

## v1.0.1
2017-07-11

* [fixed] Asset manager. Cannot change version of versions with a sequence component.

## v1.0.0
2017-07-07

* [fixed] API. Errors in hooks are shown as event hub errors.
* [fixed] Ui, Asset manager. Asset manager fails to open in some rare cases.
* [fixed] API. Application search on disk does not follow symlinks.
* [changed] Events, API. The ftrack.connect.application.launch event is now also emitted through the new api. The event allows you to modify the command and/or environment of applications before they are launched.
* [changed] API. Changed Connector based plugins to use the new API to publish assets.
* [fixed] Ui, Import asset. Import asset dialog errors when a version has no user.
* [changed] API. Changed from using legacy API locations to using locations from the ftrack-python-api. Make sure to read the migration notes before upgrading.
* [fixed] Internal. Fixed occasional X11 related crashes when launching actions on Linux.
* [changed] Publish. The new api and locations are used
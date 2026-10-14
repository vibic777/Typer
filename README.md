# Typer
[Русский](#русский) · [English](#english)

> Готовый текст не стоит набирать заново, если форма не принимает вставку.

**GitHub About / English:** Types a prepared text into the active Windows field when a form will not accept paste, such as an appeal or a complaint. No clipboard and no network.
**Описание GitHub / Русский:** Печатает готовый текст в активное поле Windows, когда форма не даёт вставить обращение или жалобу. Без буфера обмена и без сети.

## Русский

**Typer** — прикладной инструмент для Windows. Его сделали для сайтов и форм, где копирование и вставка закрыты и текст просят перепечатать вручную: обращение, жалоба, уже написанное заявление. Программа берёт локальный TXT и вводит его в активное поле как нажатия клавиш, чтобы не мучиться.

Она не забирает текст со страницы, не снимает защиту и не открывает закрытый доступ. Это набор своего текста туда, куда его и так разрешено ввести с клавиатуры.

## Возможности

- Вводит текст в активное поле как последовательность нажатий клавиш.
- Не использует буфер обмена и не подключается к сети во время работы.
- Поддерживает TXT в кодировках UTF-8, UTF-16 и Windows-1251.
- Показывает предпросмотр, ход ввода и позволяет остановить процесс.
- Позволяет настроить задержку между символами для совместимости с медленными полями ввода.

Программа работает в Windows и использует встроенные Python-модули Tkinter и Windows API. Для запуска из исходников нужен Python 3 с Tkinter. Для portable-сборки используется PyInstaller; на другом компьютере Python не требуется.

## Как пользоваться

1. Запустите `start_typer.bat` (нужен Python 3 с Tkinter) или portable-файл `dist/Typer.exe`.
2. Нажмите **«Выбрать TXT…»** и выберите текстовый файл.
3. Просмотрите загруженный текст и при необходимости настройте задержку в миллисекундах. Ноль означает максимально быструю отправку.
4. Перейдите в целевое приложение и установите курсор в поле, куда разрешено вводить текст.
5. Нажмите **Ctrl+Shift+C**. Typer дождётся отпускания клавиш и начнёт ввод в активное поле.
6. Для остановки нажмите **Ctrl+Shift+X**. Не переключайте фокус в другое окно во время ввода: текст поступает в то поле, которое активно в данный момент.

Если приложение теряет символы, увеличьте задержку, например до 30–50 мс. Перенос строки отправляется как клавиша Enter; поведение зависит от целевого поля. Эмодзи и отдельные символы могут обрабатываться различными приложениями по-разному.

## Назначение и правомерное использование

Некоторые приложения и сайты отключают копирование или вставку. Это может создавать трудности при работе с материалами, к которым пользователь уже имеет законный доступ, а также для людей, которым удобнее использовать альтернативный способ ввода. Typer помогает вручную перенести предоставленный пользователем текст в активное поле, когда такой ввод допустим.

Typer не определяет, кому принадлежит текст и разрешено ли его повторное использование. Пользователь отвечает за наличие прав или иных законных оснований для копирования, ввода, хранения и передачи текста. Соблюдайте авторские и смежные права, условия лицензии и использования сервиса, требования конфиденциальности, защиты персональных данных и информационной безопасности. Не используйте программу для обхода DRM, платного доступа, технических ограничений, антибот-защиты или запретов, установленных владельцем сервиса. При сомнениях запросите разрешение или воспользуйтесь доступным официальным способом экспорта либо альтернативным форматом.

Описание возможных неудобств не является юридическим заключением и не означает, что ограничение копирования автоматически нарушает чьи-либо права. Правовая оценка зависит от юрисдикции, типа материала, характера доступа и конкретных обстоятельств.

## Сборка portable EXE

Запустите `build.bat`. Скрипт создаст локальное окружение сборки, установит PyInstaller и Pillow, сгенерирует иконки из `build_icon.py` и соберёт `dist/Typer.exe`. Если подходящего Python с Tkinter нет, скрипт автоматически скачает официальный runtime с python.org. Для очистки временных файлов запустите `clean.bat`; спецификация PyInstaller сохраняется.

## Конфиденциальность

Typer читает выбранный файл локально и отправляет его содержимое в активное окно как клавиатурный ввод. Программа не передаёт текст на сервер и не сохраняет копию файла. Учитывайте, что целевое приложение или сайт может обрабатывать и сохранять введённый текст согласно своим настройкам и правилам.

---

<a id="english"></a>

## English

**Typer** is a practical Windows tool. It is for forms and sites that block paste and ask you to retype a text you already wrote: an appeal, a complaint, a prepared statement. Typer reads a local TXT file and types it into the active field as keystrokes, so you do not have to do that by hand.

It does not pull text from the page, remove protection, or open access that is closed. It types your own text into a field where keyboard entry is already allowed. Its icon shows a keyboard and a caret.

### Features

- Types text into the active field as keyboard input.
- Does not use the clipboard or connect to the network while running.
- Supports TXT files encoded as UTF-8, UTF-16, or Windows-1251.
- Provides a preview, progress status, and a stop shortcut.
- Lets you adjust the per-character delay for compatibility with slower input fields.

Typer runs on Windows and uses the built-in Python Tkinter module and Windows API. Running from source requires Python 3 with Tkinter. The portable build uses PyInstaller and does not require Python on the target computer.

### How to use

1. Run `start_typer.bat` (requires Python 3 with Tkinter) or the portable `dist/Typer.exe`.
2. In the current build, the application interface is in Russian: click **«Выбрать TXT…»** and select a text file.
3. Review the preview and, if needed, set the delay in milliseconds. Zero sends input as fast as possible.
4. Switch to the target application and place the caret in a field where you are allowed to enter the text.
5. Press **Ctrl+Shift+C**. Typer waits for the shortcut keys to be released, then starts typing into the active field.
6. Press **Ctrl+Shift+X** to stop. Keep the intended field focused while typing; input goes to whichever field is active.

If characters are missed, increase the delay, for example to 30–50 ms. Line breaks are sent as Enter key presses, and the target field determines how they behave. Emoji and some special characters may be handled differently by different applications.

### Purpose and lawful use

Some applications and websites disable copying or pasting. This can make it harder to work with material a user can lawfully access, or to use an alternative input method. Typer helps transfer user-provided text into the active field when that input is permitted.

Typer cannot determine who owns the text or whether reuse is authorized. You are responsible for having the rights or other lawful basis to copy, enter, store, and transmit the text. Respect copyright and related rights, license and service terms, privacy and data-protection requirements, and information-security rules. Do not use the program to bypass DRM, paid access, technical restrictions, anti-bot protections, or restrictions imposed by a service owner. If in doubt, request permission or use an official export option or alternative format.

This description of possible inconvenience is not legal advice and does not mean that a copy restriction automatically violates anyone's rights. The legal position depends on the jurisdiction, the material, the type of access, and the circumstances.

### Build the portable executable

Run `build.bat`. The script creates a local build environment, installs PyInstaller and Pillow, generates the icons from `build_icon.py`, and builds `dist/Typer.exe`. If no suitable Python installation with Tkinter is available, it automatically downloads the official runtime from python.org. Run `clean.bat` to remove temporary build files; the PyInstaller spec is preserved.

### Privacy

Typer reads the selected file locally and sends its contents to the active window as keyboard input. It does not upload the text to a server or save another copy of the file. The target application or website may process and store the entered text under its own settings and terms.

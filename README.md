# BallonTranslator
Ще один комп’ютерний інструмент перекладу коміксів/манги на основі глибокого навчання.

<img src="doc/src/ui0.jpg" div align=center>

<p align=center>
preview
</p>

# Особливості
* Повністю автоматизований переклад
   - Підтримка автоматичного виявлення, розпізнавання, видалення та перекладу тексту, загальна продуктивність залежить від цих модулів.
   - літерування базується на оцінці форматування оригінального тексту.
   - Пристойно працює з мангою та коміксами.
   — Покращено мангу->англійська, англійська->китайська верстка (на основі виділення областей повітряних куль.).
  
* Редагування зображень
   - Підтримка редагування маски та малювання (щось на кшталт інструмента пензля відновлення плям у PS)
   - Адаптовано до зображень із екстремальним співвідношенням сторін, таких як веб-мультфільми
  
* Редагування тексту
   - Підтримка форматування форматованого тексту та стилів тексту, перекладені тексти можна редагувати в інтерактивному режимі.
   - Підтримка пошуку та заміни
   — Підтримка експорту/імпорту в/з документів Word

# Використання

Користувачі Windows можуть завантажити Ballonstranslator-x.x.x-core.7z із [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) або [Google Drive](https://drive.google.com/drive/ folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing)(примітка: вам також потрібно завантажити останню версію Ballontranslator-1.3.xx з GitHub і розпакувати її, щоб перезаписати **Ballontranslator-1.3.0-core** або старішу інсталяцію, щоб отримати додаток оновлено.)

## Запустіть вихідний код

```bash

# Clone this repo
$ git clone https://github.com/dmMaze/BallonsTranslator.git ; cd BallonsTranslator

# install requirements_macOS.txt on macOS
$ pip install -r requirements.txt
```

Download the **data** folder from [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) or [Google Drive](https://drive.google.com/drive/folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing) and move it into BallonsTranslator/ballontranslator, finally run
```bash
# For Linux or MacOS users, see [this script](https://github.com/dmMaze/BallonsTranslator/blob/master/ballontranslator/scripts/download_models.sh) and run to download ALL models
python ballontranslator
```

## Повністю автоматизований переклад
**Рекомендується запускати програму в терміналі, якщо вона вийшла з ладу та не залишила жодної інформації, дивіться наступний малюнок.** Будь ласка, виберіть потрібний перекладач і встановіть вихідну та цільову мови під час першого запуску програми. Відкрийте папку з зображеннями, які потребують перекладу, натисніть кнопку «Виконати» і дочекайтеся завершення процесу.
<img src="doc/src/run.gif">

Формати шрифтів, наприклад розмір і колір шрифту, визначаються програмою автоматично під час цього процесу. Ви можете заздалегідь визначити ці формати, змінивши відповідні параметри з «вирішувати програмою» на «використовувати глобальні налаштування» на панелі конфігурації->Написи. (глобальні параметри — це ті формати, які відображаються на правій панелі форматування шрифту, коли ви не редагуєте жодного текстового блоку в сцені)

## Виявлення тексту
Підтримка визначення тексту англійською та японською мовами, навчальний код та додаткові відомості можна знайти на [comic-text-detector](https://github.com/dmMaze/comic-text-detector)

## OCR
  * Модель розпізнавання тексту mit_32px взята з manga-image-translator, підтримує розпізнавання англійської та японської мов і виділення кольору тексту.
  * Модель розпізнавання тексту mit_48px взято з manga-image-translator, підтримує розпізнавання англійською, японською та корейською мовами та виділення кольору тексту.
  * [manga_ocr](https://github.com/kha-white/manga-ocr) походить від [kha-white](https://github.com/kha-white), розпізнавання тексту для японської мови з основним японська манга.

## Малювання
   * AOT походить від manga-image-translator.
   * PatchMatch — це алгоритм із [PyPatchMatch](https://github.com/vacancy/PyPatchMatch), ця програма використовує [модифіковану версію](https://github.com/dmMaze/PyPatchMatchInpaint) мною. (Adobe використовує цей алгоритм)
  

## Перекладачі

  * <s> Змініть URL-адресу перекладача goolge з *.cn на *.com, якщо вас не заблокував GFW. </s> Google припиняє роботу служби перекладу в Китаї, будь ласка, встановіть відповідну URL-адресу на панелі конфігурації на *.com.
  * Для перекладача Caiyun потрібен [токен](https://dashboard.caiyunapp.com/).
  * Папаго.
  * Перекладач DeepL & Sugoi (і це перетворення перекладу CT2) завдяки [Snowad14](https://github.com/Snowad14).

  Щоб додати новий перекладач, зверніться до [how_to_add_new_translator](doc/how_to_add_new_translator.md), це просто як підклас BaseClass і реалізація двох інтерфейсів, потім ви можете використовувати його в програмі, ви можете зробити свій внесок у проект.

## Previews of fully automated translation results
|            Original            |         Translated (CHS)         |         Translated (ENG)         |
| :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: |
|![Original](ballontranslator/data/testpacks/manga/original2.jpg 'https://twitter.com/mmd_96yuki/status/1320122899005460481')| ![Translated (CHS)](doc/src/result2.png) | ![Translated (ENG)](doc/src/original2_eng.png) |
|![Original](ballontranslator/data/testpacks/manga/original3.jpg 'https://twitter.com/_taroshin_/status/1231099378779082754')| ![Translated (CHS)](doc/src/original3.png) | ![Translated (ENG)](doc/src/original3_eng.png) |
| ![Original](ballontranslator/data//testpacks/manga/AisazuNihaIrarenai-003.jpg) | ![Translated (CHS)](doc/src/AisazuNihaIrarenai-003.png) | ![Translated (ENG)](doc/src/AisazuNihaIrarenai-003_eng.png) |
|           ![Original](ballontranslator/data//testpacks/comics/006049.jpg)           | ![Translated (CHS)](doc/src/006049.png) | |

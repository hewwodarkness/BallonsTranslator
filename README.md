# BallonTranslator
Ще один комп’ютерний інструмент перекладу коміксів/манги на основі глибокого навчання.

<img src="doc/src/ui0.jpg" div align=center>

<p align=center>
preview
</p>

# Використання

Користувачі Windows можуть завантажити Ballonstranslator-x.x.x-core.7z із [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) або [Google Drive](https://drive.google.com/drive/folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing)
Примітка: вам також потрібно завантажити останню версію Ballontranslator-1.3.xx з GitHub і розпакувати її, щоб перезаписати **Ballontranslator-1.3.0-core** або старішу інсталяцію, щоб отримати останнє оновлення)

## Запустити код

```bash

# Clone this repo
$ git clone https://github.com/dmMaze/BallonsTranslator.git ; cd BallonsTranslator

# install requirements_macOS.txt on macOS
$ pip install -r requirements.txt
```

## Перекладачі

  * <s> Змініть URL-адресу перекладача goolge з *.cn на *.com, якщо вас не заблокував GFW. </s> Google припиняє роботу служби перекладу в Китаї, будь ласка, встановіть відповідну URL-адресу на панелі конфігурації на *.com.
  * Для перекладача Caiyun потрібен [токен](https://dashboard.caiyunapp.com/).
  * Папаго.
  * Перекладач DeepL & Sugoi (і це перетворення перекладу CT2) завдяки [Snowad14](https://github.com/Snowad14).

  Щоб додати новий перекладач, зверніться до [how_to_add_new_translator](doc/how_to_add_new_translator.md), це просто як підклас BaseClass і реалізація двох інтерфейсів, потім ви можете використовувати його в програмі, ви можете зробити свій внесок у проект.
  
## Previews of fully automated translation results
|            Original            |         Translated (CHS)         |
| :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: |
|![Original](ballontranslator/data/testpacks/manga/original2.jpg 'https://twitter.com/mmd_96yuki/status/1320122899005460481')|  ![original2](https://github.com/hewwodarkness/BallonsTranslator/assets/66019326/e611992a-869e-4466-83b3-5dc3e983326a) |

|            Original            |         Translated (CHS)         |
| :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: |
|![ea41e72fcd3049014913ec46f43ea1a7](https://github.com/hewwodarkness/BallonsTranslator/assets/66019326/6a206c63-fd9f-4370-be72-c6eea3a12d15)| ![ea41e72fcd3049014913ec46f43ea1a7](https://github.com/hewwodarkness/BallonsTranslator/assets/66019326/7df8e707-3ca1-4321-a871-86d7d334723c) |

# BallonTranslator
Ще один комп’ютерний інструмент перекладу коміксів/манги на основі глибокого навчання.


ЦЕ НЕ МІЙ ПРОЄКТ, просто хотілося донести в маси швидкий автоматичний перекладач манги, який перекладає з англійської та інших мов на українську мову.
<img src="doc/src/ui0.jpg" div align=center>

# Використання

Користувачі Windows можуть завантажити Ballonstranslator-x.x.x-core.7z із [MEGA](https://mega.nz/folder/gmhmACoD#dkVlZ2nphOkU5-2ACb5dKw) або [Google Drive](https://drive.google.com/drive/folders/1uElIYRLNakJj-YS0Kd3r3HE-wzeEvrWd?usp=sharing)

Примітка: Вам також потрібно завантажити останню версію Ballontranslator-1.3.xx з GitHub і розпакувати її, щоб перезаписати **Ballontranslator-1.3.0-core** або старішу інсталяцію, щоб отримати останнє оновлення

## Запустити код

```bash
# Clone this repo
$ git clone https://github.com/dmMaze/BallonsTranslator.git ; cd BallonsTranslator

# install requirements_macOS.txt on macOS
$ pip install -r requirements.txt
```
Якщо вам теж встановило усі плагіни крім pkuseg використайте ось це:

```bash
pip install https://pypi.tuna.tsinghua.edu.cn/simple pkuseg
```
## Важлива інформація

Для красивого тексту використовуйте шрифти:
- MP Manga Font Bold
- Anime Ace v05

Налаштування для перекладу манги:
- DL MODULE

      ctd, 1280, 4, cuda
- OCR

      mit32px, 16, cuda
- Inpaint

      aot, 2048, cuda
## Результати перекладу
|            Оригінал            |         Переклад українською         |
| :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: |
|![Original](ballontranslator/data/testpacks/manga/original2.jpg 'https://twitter.com/mmd_96yuki/status/1320122899005460481')|  ![original2](https://github.com/hewwodarkness/BallonsTranslator/assets/66019326/e611992a-869e-4466-83b3-5dc3e983326a) |

|            Оригінал            |         Переклад українською          |
| :-----------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------: |
|![ea41e72fcd3049014913ec46f43ea1a7](https://github.com/hewwodarkness/BallonsTranslator/assets/66019326/6a206c63-fd9f-4370-be72-c6eea3a12d15)| ![ea41e72fcd3049014913ec46f43ea1a7](https://github.com/hewwodarkness/BallonsTranslator/assets/66019326/7df8e707-3ca1-4321-a871-86d7d334723c) |

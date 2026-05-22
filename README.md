# Klippare

Klippare är en webbapp som hjälper till när man har ett bildark med flera ikoner, loggor eller små motiv på samma bild. I stället för att klippa ut varje motiv för hand laddar man upp bildarket i appen, väljer några enkla inställningar och låter appen hitta motiven automatiskt.

När appen är klar får man tillbaka varje hittat motiv som en egen PNG-bild. Alla bilder packas också i en ZIP-fil, så att resultatet går att ladda ner direkt.

## Vad appen gör

Appen tar emot en eller flera bilder i formaten PNG, JPG, JPEG eller WEBP. Den analyserar bilden med OpenCV, försöker hitta separata motiv på arket och beskär sedan ut dem en och en. Resultatet sparas tillfälligt på servern, visas på resultatsidan och kan laddas ner som en ZIP-fil.

Det här är användbart om man till exempel har ett stort ark med många små symboler, produktbilder, loggor eller ikoner och vill få ut dem som separata filer utan att sitta och markera varje ruta manuellt.

## Så används appen

1. Öppna appen i webbläsaren.
2. Ladda upp ett eller flera bildark.
3. Välj preset om standardinställningen inte passar.
4. Ändra eventuellt hur bilderna ska hittas på arket.
5. Välj hur de färdiga bilderna ska se ut, till exempel om de ska göras kvadratiska.
6. Klicka på `Klipp bilder`.
7. Ladda ner ZIP-filen med alla färdiga PNG-bilder.

## Inställningarna i korthet

`PADDING` betyder extra luft runt varje bild som klipps ut. Högre värde ger mer marginal runt motivet.

`MIN_AREA` bestämmer hur litet något får vara för att räknas som en riktig bild. Om småskräp blir egna bilder kan värdet höjas. Om små ikoner missas kan värdet sänkas.

`THRESHOLD_VALUE` hjälper appen att skilja bakgrund från motiv. Det kan behöva justeras om bilden är ljus, brusig eller har svag kontrast.

`MORPH_CLOSE` hjälper appen att koppla ihop delar som hör till samma motiv.

`DILATE` gör masken lite större så att text, ram och symboler hålls ihop.

## Driftinformation

- Domän: `example.com`
- Intern port: `127.0.0.1:8000`
- Projektkatalog: `/var/www/klippare`
- Virtualenv: `/var/www/klippare/venv`
- systemd service: `klippare.service`
- Max uppladdning: 80 MB
- Gamla jobb rensas efter 24 timmar

## Lokal körning på VPS

```bash
cd /var/www/klippare
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 127.0.0.1:8000 app:app
```

Kontrollera att appen svarar:

```bash
curl http://127.0.0.1:8000/health
```

## Viktiga filer

- `app.py` hanterar webbsidor, uppladdning, resultat och nedladdning.
- `cropper.py` innehåller själva bildanalysen och beskärningen med OpenCV.
- `config.py` innehåller sökvägar, tillåtna filtyper, maxstorlek och presets.
- `cleanup.py` rensar gamla jobb från `storage/`.
- `templates/` innehåller HTML-sidorna.
- `static/css/style.css` innehåller designen.
- `static/js/app.js` fyller i inställningar när man byter preset.
- `storage/` används för uppladdade bilder, resultat och ZIP-filer.
- `scripts/` innehåller hjälpscript för installation och drift.

## Kort sagt

Klippare finns för att göra ett tråkigt manuellt jobb snabbare: ladda upp ett bildark, låt appen hitta motiven och hämta hem alla utklippta bilder som separata PNG-filer.

## GitHub-version

En ren GitHub-version ska inte innehålla `venv/`, uppladdade bilder, resultatbilder eller ZIP-filer från körningar. De mapparna skapas/töms via `storage/` och hålls i repot med `.gitkeep`.

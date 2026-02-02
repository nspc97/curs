# Instrucțiuni Proiect Mini Curs Valutar

Acest proiect este un site static pentru calculul cursului valutar, optimizat pentru SEO și pregătit pentru Google AdSense.

## 1. Configurare Imagini
- **Favicon**: Fișierul `assets/favicon.svg` este deja creat.
- **Preview Image**: Pentru ca site-ul să arate bine când distribui link-ul pe Facebook/WhatsApp, adaugă o imagine atractivă (recomandat 1200x630px) în folderul `assets` și numește-o `preview-image.jpg`.

## 2. Google AdSense
Pentru a afișa reclame și a câștiga bani:
1. Creează un cont pe [Google AdSense](https://www.google.com/adsense/start/).
2. Adaugă site-ul tău în contul AdSense.
3. Copiază scriptul primit de la Google.
4. Deschide `index.html` și caută comentariul `<!-- Adăugați scriptul AdSense aici mai târziu -->`.
5. Lipește scriptul acolo.
6. În `index.html`, blocurile `<div class="ad-placeholder">` sunt locurile unde poți pune codul pentru unitățile de reclame specifice (Display Units).

## 3. Publicare
Fiind un site static ("fără backend"), îl poți găzdui gratuit pe:
- **GitHub Pages** (Recomandat)
- Netlify
- Vercel

## Notă despre Cursul Valutar
Deoarece site-urile statice nu pot accesa direct serverele BNM din cauza restricțiilor de securitate (CORS), acest site folosește un API gratuit, rapid și fiabil (`fawazahmed0/currency-api`) care oferă rate de schimb agregate de pe piață. Acestea sunt foarte apropiate de cele oficiale.

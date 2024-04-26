Locul2 - Sesiunea de comunicari stiintifice

Aceasta reprezintă o aplicaţie care utilizează o rețea neuronală de tipul YOLOv3 pentru a detecta și recunoaște plăcile de înmatriculare dintr-un set de imagini. Pentru a face acest lucru, codul încarcă modelul YOLOv3, definește directoarele cu fișierele de configurație și listele de clase, încarcă imaginea din fiecare fișier din directorul specificat și aplică rețeaua neuronală pentru a detecta plăcile de înmatriculare. După detectare, plăcile de înmatriculare sunt preluate, transformate în imagini alb-negru și scanate cu ajutorul bibliotecii EasyOCR pentru a recunoaște caracterele din placa de înmatriculare.

Dacă există o potrivire cu placa de înmatriculare a unei mașini raportate ca fiind furată într-o bază de date MySQL, aplicația va trimite un e-mail la o adresă specificată și va actualiza coordonatele geografice ale mașinii în baza de date. În caz contrar, aplicația va continua să ruleze și va trece la detectarea plăcilor de înmatriculare din următoarea imagine din directorul specificat.

Pentru a face aceasta, codul utilizează și biblioteca Geocoder pentru a obține coordonatele geografice ale utilizatorului care rulează aplicația și biblioteca SMTPlib pentru a trimite e-mailul către adresa specificată.

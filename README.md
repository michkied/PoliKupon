# PoliKupon

PoliKupon to bot Discordowy obsługujący system Polilicealnikowych kuponów na nieprzygotowanie w czasie nauki zdalnej.
Program napisany jest w języku Python (3.8) i wykorzystuje bazę danych PostgreSQL.
Bot stworzony został z myślą o pracy na maszynie z systemem Linux, tak więc działanie na innych systemach operacyjnych może wymagać zmian w kodzie.
Dane konfiguracyjne znajdują się w pliku `config.ini`. W razie pytań/sugestii zgłoś się do nas przez zakładkę Issues lub na serwerze Discord bota.

### Komendy bota:

##### Dla uczniów:
`.kupon` -  Rozpoczyna proces wykorzystania kuponu

`.moje_kupony` - Wyświetla liczbę posiadanych kuponów

`.pomoc` - Wyświetla instrukcję korzystania z bota

##### Dla moderatorów kuponów:
`.nowy_kupon <@użytkownik> <imię> <nazwisko> <klasa>` - Rejestruje nowy kupon

`.kupony` - Wyświetla listę zarejestrowanych kuponów

`.usun_kupon <ID użytkownika>` - Usuwa kupon danego użytkownika

`.archiwizuj [nazwa kanału]` - Archiwizuje kanał po zakończonych zakupach

##### Dla właściciela bota:
`.keys` - Zarządza kluczami serwerów

`.killapp` - Wyłącza bota 

Tech stack
1. Bahasa Pemrograman & Library Utama
Python: Bahasa dasar yang digunakan untuk membangun logika parser.
Pyparsing: Ini adalah stack paling krusial di sini. Pyparsing adalah library Python yang digunakan untuk membuat Grammar (tata bahasa) guna menganalisis teks terstruktur tanpa perlu menulis Regular Expression (Regex) yang rumit.

2. Komponen Logika (Parsing Logic)
pp.Suppress & pp.Word(pp.nums): Digunakan untuk mengambil nilai "priority" (angka di dalam kurung sudut seperti <13>) tetapi membuang tanda kurungnya.
pp.Combine & pp.alphanums: Digunakan untuk menggabungkan karakter alfanumerik menjadi satu kesatuan nama objek atau nilai.
pp.quotedString: Digunakan agar parser bisa membaca nilai yang berada di dalam tanda kutip (contoh: name="Gemini AI").
Key-Value Assignment (assgn): Logika untuk mendeteksi pola kunci=nilai (misal: user=admin).

3. Data Structure & Error Handling
Python Dictionary (dict): Hasil akhir dari ekstraksi log disimpan dalam format Dictionary (kunci-nilai), yang mempermudah pengambilan data di tahap selanjutnya.
Exception Handling (pp.ParseException): Menggunakan blok try-except untuk menangkap kesalahan jika format log yang dibaca tidak sesuai dengan aturan yang sudah dibuat.

/* Menampilkan tanggal & jam real-time yang update setiap detik */
const HARI_ID = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];
const BULAN_ID = [
  "Januari", "Februari", "Maret", "April", "Mei", "Juni",
  "Juli", "Agustus", "September", "Oktober", "November", "Desember",
];

function pad(n) {
  return n.toString().padStart(2, "0");
}

function updateClock() {
  const now = new Date();
  const tanggalStr = `${HARI_ID[now.getDay()]}, ${now.getDate()} ${BULAN_ID[now.getMonth()]} ${now.getFullYear()}`;
  const jamStr = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

  document.querySelectorAll("[id^='tanggal-header']").forEach((el) => (el.textContent = tanggalStr));
  document.querySelectorAll("[id^='jam-header']").forEach((el) => (el.textContent = jamStr));
}

updateClock();
setInterval(updateClock, 1000);

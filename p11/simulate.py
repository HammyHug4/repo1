import concurrent.futures
import xmlrpc.client

APP_NODES = [
    "http://app1:8000/",
    "http://app2:8000/",
    "http://app3:8000/",
]

def send_insert_request(node_url, user_id, nama, umur):
  try:
    proxy = xmlrpc.client.ServerProxy(node_url, allow_none=True)
    print(
        f"[SIMULASI] Mengirim data ke {node_url} (User ID: {user_id}, Nama:"
        f" {nama})"
    )
    result = proxy.tambah_user(user_id, nama, umur)
    print(f"[HASIL] Respon dari {node_url}: {result}")
  except Exception as e:
    print(f"[ERROR] Gagal terhubung ke {node_url}: {e}")

if __name__ == "__main__":
  print("=== MEMULAI SIMULASI REQUEST KONKUREN KE 3 APP NODE ===")
  target_id = 3
  target_name = "UserKonkuren"
  target_age = 25

  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    for i, url in enumerate(APP_NODES):
      executor.submit(send_insert_request, url, target_id, f"Nama_{i+1}", 25)
  print("=== SIMULASI SELESAI ===")

import streamlit as st
from uuid import uuid4 as uuid
import requests
from time import sleep

API_URL = "https://m1ragczl27.execute-api.us-east-1.amazonaws.com"


def main():
    st.title("Interface de Extração de Informações de Imagem Utilizando o Bedrock")
    st.header("Envie uma ou mais imagens:")

    files = st.file_uploader(
        "Envie as imagens",
        type=["PNG", "PDF", "JPEG", "JPG"],
        accept_multiple_files=True,
        key="new",
    )

    prompt = st.text_area("Digite o prompt:")

    if files and prompt:
        if st.button("Obter Resposta"):
            for file in files:
                process_id = str(uuid())
                signed_url = get_signed_url(process_id, file)
                upload_file(signed_url, file)
                start_process(prompt, signed_url['key'], process_id)
                check_process_status(process_id)


def get_signed_url(process_id, file):
    file_name = file.name
    file_type = file.type
    name = file_name.rpartition(".")[0]
    payload = {
        "process_id": process_id,
        "files": [{"name": name, "type": file_type, "filename": file_name}],
    }
    response = requests.post(f"{API_URL}/dev/signed-url", json=payload)
    return response.json()[name]


def upload_file(signed_url, file):
    try:
        url = signed_url["url"]
        with file as f:
            headers = {"Content-Type": file.type}
            response = requests.put(url, data=f, headers=headers)
        return response
    except Exception as e:
        st.error(f"Erro ao fazer upload do arquivo: {e}")


def start_process(prompt, key, process_id):
    payload = {
        "process_id": process_id,
        "source_pdf_key": key,
        "operation": "textract",
        "webhook_url": "https://webhook-test.com/d53e84f440670f8f4840a6f49883a664",
        "prompt": prompt,
    }
    response = requests.post(f"{API_URL}/dev/process", json=payload)
    return response


def check_process_status(process_id):
    while True:
        response = requests.get(f"{API_URL}/dev/get-response/{process_id}")
        if response.status_code != 200:
            print("Erro na requisição")
            sleep(2)
        else:
            data = response.json()
            if "error" in data:
                st.error("Erro no processamento")
                sleep(2)
            else:
                st.success("Processamento concluído com sucesso")
                st.write(data["textractPayload"])
                break


if __name__ == "__main__":
    main()

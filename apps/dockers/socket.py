import pty
import os
import asyncio
import re
import subprocess

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

router: APIRouter = APIRouter()

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x1B][\[()#;?]*[0-9]*[A-Za-z]?)')
hash_pattern = re.compile(r'^\s*#\s*$', re.MULTILINE)

@router.websocket("/containers/{container_id}")
async def interactively_connect_with_container(socket: WebSocket, container_id: str):
    await socket.accept()
    try:

        main_fd, sub_fd = pty.openpty()
        subprocess.Popen(
            ['docker', 'exec', '-it', container_id, 'sh']
            , stdin=sub_fd
            , stdout=sub_fd
            , stderr=sub_fd
            , close_fds=True
        )

        os.close(sub_fd)
        sa = os.read(main_fd, 1024).decode('utf-8')
        a = hash_pattern.sub('', sa)
        await socket.send_text(a)

        buffer = ''
        prompt_detected = False
        while True:
            try:
                req_cmd = await socket.receive_text()
                os.write(main_fd, f'{req_cmd}\n'.encode())
            except WebSocketDisconnect:
                print("Client disconnected")
                break

            try:
                while True:
                    output = os.read(main_fd, 1024).decode('utf-8')
                    if not output:
                        break
                    buffer += output
                    if '#' in buffer:
                        prompt_detected = True
                        break
                    await asyncio.sleep(1)

                if buffer:
                    clean_output = ansi_escape.sub('', buffer)
                    clean_output = hash_pattern.sub('', clean_output)
                    clean_output = re.sub(r'^\s*$', '', clean_output, flags=re.MULTILINE)
                    await socket.send_text(clean_output)
                    buffer = ""

                if prompt_detected:
                    buffer = ""

            except Exception as e:
                print("Error reading from pty:", e)
                break

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("err")
        print(e)
        await socket.close()


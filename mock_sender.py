from named_pipes import PipeSender
from time import sleep

print('[MockSender]: Starting...')
pipe = PipeSender()
pipe.connect()
sleep(5)
pipe.send(['R'])
sleep(1)
pipe.send(['L\''])
sleep(0.003)
pipe.send(['R2'])
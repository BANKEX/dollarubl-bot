# coding=utf-8
import random
import requests
from tornkts import utils

from roboman.bot import BaseBot


class KTSBot(BaseBot):
    name = 'kts'
    key = '116835760:AAGuIPvUFUhAdEYpXD2QFHS04o4-h4DjF30'

    allowed_chats = [-23165158, 100538095, 1012824, -1001034638777, -148905847]

    @classmethod
    def on_hook(cls, data):
        chat_id = data.get('chat_id')
        if chat_id in cls.allowed_chats:
            if data.get('photo') is not None:
                cls._on_image(chat_id, data.get('photo'))

            text = data.get('text', '')
            if text is None:
                return

            text = text.strip()

            if text.startswith('@KTSBot'):
                text = text[len('@KTSBot'):]
                text = text.strip()

            if text.startswith('/serega'):
                var = random.choice([u'мороженое', u'шашлыки', u'чебуреки', u'пицца'])
                response = u'У Сереги в Анапе %s, можно от качалки отдохнуть!' % (var,)
            elif text.startswith('/max'):
                var = random.choice(
                    [u'за косарь', u'это еще месяц', u'это за 20 тысяч можно', u'за два вечера бахнем'])
                response = u'Ну %s.' % (var)
            elif text.startswith('/schedule'):
                response = """
                Расписание пар:
                    1 пара: 08:30 — 10:05
                    2 пара: 10:15 — 11:50
                    3 пара: 12:00 — 13:35
                    4 пара: 13:50 — 15:25
                    5 пара: 15:40 — 17:15
                    6 пара: 17:25 — 19:00
                    7 пара: 19:10 — 20:45
                """
            else:
                response = None
            if response is not None:
                requests.post(cls.get_method_url('sendMessage'), {'chat_id': chat_id, 'text': response})
        else:
            requests.post(cls.get_method_url('sendMessage'), {
                'chat_id': chat_id,
                'text': u'Извините, это закрытый бот ' + str(chat_id)
            })

    @classmethod
    def _on_image(cls, chat_id, photo):
        if len(photo) == 3:
            photo = photo[2]
        elif len(photo) == 2:
            photo = photo[1]
        elif len(photo) == 1:
            photo = photo[0]
        else:
            return

        response = requests.get(cls.get_method_url('getFile'), {
            'file_id': photo.get('file_id'),
        })

        response = utils.json_loads(response.content)
        url = cls.get_file_url(response.get('result').get('file_path'))

        response = requests.post(
            'https://api.projectoxford.ai/face/v1.0/detect?returnFaceAttributes=age,gender,headPose,smile,facialHair,glasses',
            headers={
                'Content-Type': 'application/json',
                'Ocp-Apim-Subscription-Key': '07974eb651b84489b9bd0ff0900531de'
            }, data=utils.json_dumps({'url': url}))

        response = utils.json_loads(response.content)

        if len(response) > 0:
            for face in response:
                attrs = face.get('faceAttributes')
                msg = u"Это {0}, возраст {1}".format(
                    u'мальчик' if attrs.get('gender') == 'male' else u'девочка',
                    int(attrs.get('age'))
                )
                cls.send(chat_id=chat_id, text=msg)
        else:
            cls.send(chat_id=chat_id, text=u'Тут нет людей')

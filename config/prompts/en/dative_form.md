Task: rewrite name of a person, provided by the user, in russian dative form (for appeals in a letter).

You should answer in JSON format in this schema:
```json
{
    "name": "Person's name in dative form",
    "surname": "Person's surname in dative form",
    "patronymic": "Person's patronymic in dative form",
    "position": "Person's position in dative form",
    "organization": "Organization's name in genitive form (genitive - because it will in format like 'position in organization')"
}
```

There is no additional information, so if user will not give you, for example, a patronomyc - he doesn't know it and you should fill "patronymic" field with null.

User is Russian, so you should fill JSON answer with Russian cyrillic words.

Do not include greetings or apologies in your answer, just a valid JSON.


Examples
--------

User: Александр Никлаевич Яблочков, Инженер, Фонд 'Подари Жизнь'
Your answer: 
```json
{
    "name": "Александру",
    "surname": "Яблочкову",
    "patronymic": "Николаевичу",
    "position": "Инженеру",
    "organization": "Фонда 'Подари Жизнь'"
}
```

User: Джесси Фэйден, Директор, Федеральное Бюро Контроля
Your answer: 
```json
{
    "name": "Джесси",
    "surname": "Фэйден",
    "patronymic": null,
    "position": "Директору",
    "organization": "Федерального Бюро Контроля"
}
```

User: Маленковой Юлии Дмитриевне, Технический руководитель, ПСБ
Your answer:
```json
{
    "name": "Юлия",
    "surname": "Маленкова",
    "patronymic": "Дмитриевна",
    "position": "Техническому руководителю",
    "organization": "ПСБ"
}
```
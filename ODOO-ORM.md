* [Create](#create)
* [Write](#write)
* [Unlink](#unlink)
* [Search](#search)
* [Search_count](#search_count)
* [Search_read](#search_read)
* [Browse](#browse)
* [Read](#read)
* [Read_group](#read_group)
* [Default_get](#default_get)
* [Name_get](#name_get)

## Create

`Model.create(vals_list) -> records`

- Створює нові записи для моделі.
- Нові записи ініціалізуються за допомогою значень зі списку dicts `vals_list`, якщо необхідно, з `default_get()`.

### Параметри

**vals_list** (Union[list[dict], dict]) –

значення для полів моделі, як список словників:

```python
[{'field_name': field_value, ...}, ...]
```

Для зворотної сумісності `vals_list` може бути словник. Він розглядається як одиночний список `[vals]`, і повертається
один запис.

подробиці див `write()`

### Return

створені записи

### Raises

- `AccessError` – якщо поточному користувачеві заборонено створювати записи вказаної моделі

- `ValidationError` – якщо користувач намагається ввести недійсне значення для поля вибору

- `ValueError` – якщо ім’я поля, указане у значеннях створення, не існує.

- `UserError` – якщо в ієрархії об’єктів буде створено цикл в результаті операції (наприклад, встановлення об’єкта як
  власного батьківського)

```python
@api.model_create_multi
def create(self, data_list):
    record = super().create(data_list)
    return record


@api.model_create_multi
@api.returns('self', lambda value: value.id)
def create(self, data_list):
    records = self._create(data_list)
    return records
```

---

## Write

`Model.write(vals) -> bool`

Оновлює всі записи selfнаданими значеннями.

### Параметри

**vals** ( dict ) – поля для оновлення та значення для них

### Raises

- `AccessError` – якщо користувачеві заборонено змінювати вказані записи/поля

- `ValidationError` – якщо для полів вибору вказано недійсні значення

- `UserError` – якщо в ієрархії об’єктів буде створено цикл в результаті операції (наприклад, встановлення об’єкта як
  власного батьківського)

### Other

- Для числових полів ( `Integer`, `Float`) значення має бути відповідного типу

- Для `Boolean` значення має бути a `bool`

- Для `Selection`, значення має відповідати вибраним значенням (зазвичай `str`, іноді `int`)

- Для `Many2one` значення має бути ідентифікатор бази даних запису, який потрібно встановити

- Очікуване значення поля `One2many` відношення `Many2many`– це список тих, `Commandякі` маніпулюють відношенням. Всього
  є 7 команд: `create()`, `update()`, `delete()`, `unlink()`, `link()`, `clear()` та `set()`.

- Для `Date` та `~odoo.fields.Datetime` значення має бути або датою (часом), або рядком.

---

## Unlink

`Model.unlink()`

Видаляє записи в `self`.

### Raises

`AccessError` – якщо користувачеві заборонено видалити всі надані записи

`UserError` – якщо запис є властивістю за замовчуванням для інших записів

---

## Search

`Model.search(domain[, offset=0][, limit=None][, order=None][, count=False])`

```python
def search(self, domain, offset=0, limit=None, order=None, count=False):
    res = self._search(domain, offset=offset, limit=limit, order=order, count=count)
    return res if count else self.browse(res)
```

Шукає записи на основі domain домену пошуку.

### Параметри

- `domain` – пошуковий домен . Використовуйте порожній список, щоб зіставити всі записи.

- `offset`( int ) – кількість результатів для ігнорування (за замовчуванням: немає)

- `limit` ( int ) – максимальна кількість записів для Return (за замовчуванням: усі)

- `order` ( str ) – сортування рядка

- `count` ( bool ) – якщо True, підраховує лише та повертає кількість відповідних записів (за замовчуванням: False)

### Return

максимум `limit` записів, які відповідають критеріям пошуку

### Raises

`AccessError` – якщо користувачеві заборонено доступ до запитуваної інформації

---

## Search_count

`Model.search_count(domain) → int`

Повертає кількість записів у поточній моделі, які відповідають наданому домену .

```python
@api.model
def search_count(self, domain, limit=None):
    res = self.search(domain, limit=limit, count=True)
    return res if isinstance(res, int) else len(res)
```

### Параметри

domain – пошуковий домен . Використовуйте порожній список, щоб зіставити всі записи.

limit – максимальна кількість записів для підрахунку (верхня межа) (за замовчуванням: усі)

---

## Search_read

`Model.search_read([domain], [fields], offset=0, limit=None, order=None)`

виконує пошукову операцію з наступним читанням отриманого списку записів . Він призначений для використання клієнтами
RPC і позбавляє їх від додаткової подорожі, необхідної під час пошуку з наступним читанням результатів.

---

## Browse

`Model.browse([ids]) → records`

Повертає набір записів для ідентифікаторів, наданих як параметр у поточному середовищі.

```python
self.browse([7, 18, 12])
res.partner(7, 18, 12)
```

### Параметри

**ids** (*int* or *iterable(int)* or *None*) – id(s)

### Return

набір записів | recordset

---

## Read

`Model.read([fields])`

Читає запитані поля для записів у `self` методі низького рівня/RPC

```python
def read(self, fields=None, load='_classic_read'):
    fields = self.check_field_access_rights('read', fields)
    # fetch stored fields from the database to the cache
    stored_fields = OrderedSet()
    for name in fields:
        field = self._fields.get(name)
        if not field:
            raise ValueError("Invalid field %r on model %r" % (name, self._name))
        if field.store:
            stored_fields.add(name)
        elif field.compute:
            # optimization: prefetch direct field dependencies
            for dotname in self.pool.field_depends[field]:
                f = self._fields[dotname.split('.')[0]]
                if f.prefetch is True and (not f.groups or self.user_has_groups(f.groups)):
                    stored_fields.add(f.name)
        self._read(stored_fields)

        return self._read_format(fnames=fields, load=load)
```

### Параметри

- `fields` ( list ) – імена полів для повернення (за замовчуванням усі поля)

- `load` ( str ) – режим завантаження, наразі єдиним варіантом є встановити , `None` щоб уникнути завантаження `name_get`
  полів `m2o`

### Return

list

### Raises

- `AccessError` – якщо користувачеві заборонено доступ до запитуваної інформації

- `ValueError` – якщо запитане поле не існує

---

## Read_group

`Model.read_group(domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True)`

Отримайте список записів у поданні списку, згрупованих за заданими `groupby` полями.

### Параметри

- `domain` ( list ) – пошуковий домен . Використовуйте порожній список, щоб зіставити всі записи.

- `fields` ( list ) – список полів, присутніх у списку, указаному на об’єкті. Кожен елемент є або «field» (назва поля, з
  використанням агрегації за замовчуванням), або «field:agg» (агрегованого поля з функцією агрегації «agg»), або «name:
  agg(field)» (агрегованого поля з «agg» і повернути його як "ім'я"). Можливими функціями агрегації є ті, що надаються
  PostgreSQL і 'count_distinct', з очікуваним значенням.

- `groupby` ( list ) – список описів `group_by`, за якими будуть згруповані записи. Опис групування — це або поле (тоді
  воно буде згруповано за цим полем), або рядок «field:granularity». Наразі підтримувані лише параметри «день»,
  «тиждень», «місяць», «квартал» або «рік», і вони мають сенс лише для полів дати/часу.

- `offset` ( int ) – необов’язкова кількість записів, які потрібно пропустити

- `limit` ( int ) – необов’язкова максимальна кількість записів для повернення

- `orderby` ( str ) – необов’язкова специфікація, для перевизначення природного порядку сортування груп, див. також (
  наразі підтримується лише для полів many2one)order bysearch()

- `lazy` ( bool ) – якщо true, результати групуються лише за першим groupby, а решта groupby поміщаються в ключ __
  context. Якщо false, усі groupby виконуються за один виклик.

### Returns

список словників (один словник для кожного запису), що містить:

значення полів, згрупованих за полями в groupbyаргументі

__domain: список кортежів із зазначенням критеріїв пошуку

__context: словник з аргументом likegroupby

__діапазон: (лише дата/час) словник із полем_назва: гранулярність як ключі зіставлення зі словником із ключами: «від» (
включно) і «до» (виключно) зіставлення з рядковим представленням часових меж групи

### Return type

`[{‘field_name_1’: value, …}, …]`

### Raises

`AccessError` – if user is not allowed to access requested information

---

## Default_get

`Model.default_get(fields_list) → default_values`

Повертає значення за замовчуванням для полів у `fields_list`. Значення за замовчуванням визначаються контекстом,
параметрами користувача та самою моделлю.

### Параметри

`fields_list` ( list ) – імена полів, для яких запитується за замовчуванням

### Return

словник, що зіставляє імена полів із відповідними значеннями за замовчуванням, якщо вони мають значення за
замовчуванням.

### Return type

dict

---

## Name_get

`Model.name_get(fields_list)`

Повертає текстове представлення для записів у `self`, з одним виведенням елемента на вхідний запис у тому самому
порядку.

### Увага

Хоча name_get() можна використовувати дані контексту для розширеного контекстного форматування, оскільки це реалізація
за замовчуванням, оскільки `display_name` важливо скинути поведінку до «за замовчуванням», якщо ключі контексту
порожні/відсутні.

### Return

список пар для кожного запису `(id, text_repr)`


### Return type
список `[( int , str )]`

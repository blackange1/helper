from pathlib import Path


class Menu(object):
    def __init__(self, path=None):
        self.data = []
        self.file_path = path
        self.level_shift = 0  # якщо level_shift = 1 то ## => #, ### => ##
        self.level_limit = 7  # якщо level_limit = 3, він не друкуватиме ###, #### ...

    def get_data_item(self, string) -> dict:
        string = string[:len(string) - 1]
        name = string
        level = 0  # 1-6
        for ch in string:
            if ch != '#':
                break
            level += 1
        name = name[level + 1:]
        string = string.lower()
        string = string.replace(' ', '-')
        string = string[level + 1:]
        # for ch in set('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c'):
        for ch in set('!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'):
            string = string.replace(ch, '')

        # last_id = ''
        index = 0
        count = 1
        len_data = len(self.data)

        while index < len_data:
            item = self.data[index].get('id')
            if item == string:
                # last_id = string
                break
            index += 1
        else:
            return {
                'id': string,
                'name': name,
                'level': level
            }

        index += 1
        number = set('0123456789')
        while index < len_data:
            item = self.data[index].get('id')
            if string in item:
                tail = item[len(string):]
                if tail[0] == '-':
                    if number.issuperset(set(tail[1:])):
                        last_id = item
                        count += 1
            index += 1
        return {
            'id': string + '-' + str(count),
            'name': name,
            'level': level
        }

    def add(self, string) -> None:
        rec = self.get_data_item(string)
        # print(rec)
        self.data.append(rec)

    def print(self):
        for item in self.data:
            level = item.get('level') - self.level_shift
            name = item.get('name')
            rec_id = item.get('id')
            first_ch = '-'
            if level == 1:
                first_ch = '*'
            if self.level_limit > level:
                print('  ' * (level - 1) + f'{first_ch} [{name}](#{rec_id})')

    def read_file(self):
        is_open_code = False
        with open(self.file_path) as file:
            for line in file.readlines():
                if '```' == line[:3]:
                    is_open_code = not is_open_code
                if '#' in line[0] and not is_open_code:
                    # print(line)
                    self.add(line)


CURRENT_PATH = Path.cwd()
FILE_NAME = 'REDE_ME.md'
# menu = Menu(CURRENT_PATH.joinpath(FILE_NAME))
menu = Menu(CURRENT_PATH.joinpath('PYTHON-ODOO-LEARN.md'))
menu.level_shift = 1
menu.level_limit = 2
menu.read_file()
menu.print()

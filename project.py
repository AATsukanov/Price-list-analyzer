import os
import settings


class PriceMachine:

    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 0

    def load_prices(self, file_path: str = '', indicator: str = 'price', _ctrl_info=False) -> int:
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка

            RETURNS:
                int, количество загруженных позиций
        """

        print('Загрузка прайсов...')
        if os.path.isdir(file_path):
            all_files = os.listdir(file_path)
        else:
            # загружем из текущей:
            all_files = os.listdir()

        print(f'В папке обнаружено {len(all_files)} файла(ов),', end=' ')
        all_files = [f for f in all_files if f.endswith('.csv')]
        print(f'из них {len(all_files)} *.csv-файла(ов).')

        fnames = []
        for f in all_files:
            if indicator in f:
                fnames.append(f)

        if fnames:
            print(f'Найдено {len(fnames)} подходящих по имени файла(ов).')
        else:
            print(f'ВНИМАНИЕ: подходящих файлов не обнаружено, возможно, неверный формат имен файлов.')
            return 0

        # обнуляем данные:
        self.data = []

        for fname in fnames:
            fullname = os.path.join(file_path, fname)
            with open(fullname, 'r', encoding='utf-8') as f:
                # читаем заголовки из первой строки:
                headers = f.readline().rstrip().split(sep=',')
                col_id = self._search_product_price_weight(headers)
                if _ctrl_info:
                    print(f'{fname}: {headers} <=> {col_id}')
                # читаем данные построчно:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    # собираем name, price, weight, fname, pure_price в строку-словарь:
                    row = {}
                    line_as_list = list(line.rstrip().split(sep=','))
                    row['name']: str = line_as_list[col_id[0]]
                    row['fname']: str = fname
                    try:
                        row['price']: float = float(line_as_list[col_id[1]])
                        row['weight']: float = float(line_as_list[col_id[2]])
                        row['pure_price']: float = row['price'] / row['weight']
                    except Exception as exc:
                        print(f'ОШИБКА: в файле {fname} значение не может быть переведено в число:\n{exc}')
                        print('Пропускаем эту позицию.')
                        continue

                    self.data.append(row)
                    if _ctrl_info:
                        print(f"{row['fname']} {row['name']} {row['pure_price']}")
        return len(self.data)

    def _search_product_price_weight(self, headers: list[str]) -> list[int]:
        """
            Возвращает номера столбцов,
            проверки на отсутствие конкретного варианта в этой версии нет
        """
        cols = [-1, -1, -1]

        for i, col in enumerate(headers):
            if col.strip() in settings.product_col_names:
                cols[0] = i  # поиск столбца с названием
            elif col.strip() in settings.price_col_names:
                cols[1] = i  # поиск столбца с ценой
            elif col.strip() in settings.weight_col_names:
                cols[2] = i  # поиск столбца с весом

        if -1 in cols:
            print('ВНИМАНИЕ: нужный столбец не найден.')

        return cols

    def export_to_html(self, file_name: str = 'output.html', data=None):
        if data is None:
            # по-умолчанию показываем все данные:
            data = self.data

        result = settings.output_header_html

        for n, row in enumerate(data):
            result += '\t\t<tr>\n'
            result += f'\t\t\t<td>{n + 1}</td>\n'
            result += f'\t\t\t<td>{row["name"]}</td>\n'
            result += f'\t\t\t<td>{row["price"]}</td>\n'
            result += f'\t\t\t<td>{row["weight"]}</td>\n'
            result += f'\t\t\t<td>{row["fname"]}</td>\n'
            result += f'\t\t\t<td>{round(row["pure_price"], 2)}</td>\n'
            result += '\t\t</tr>\n'
        result += '\t\t</table>\n'
        result += '\t</body>\n</html>'

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f'Результат сохранен в файл {file_name}.')

    def find_text(self, text: str) -> list:
        # фильтруем:
        result = filter(lambda row: text in row['name'].lower(), self.data)

        # делаем список и сортируем:
        result = list(result)
        return sorted(result, key=lambda row: row['pure_price'])

    def show_data(self, data=None) -> None:
        if data is None:
            # по-умолчанию показываем все данные:
            data = self.data

        print('№\tНаименование\tцена\tвес\tфайл\tцена за кг')
        for j, row in enumerate(data):
            print(f'{j + 1}\t{row["name"]}\t{row["price"]}\t{row["weight"]}\t{row["fname"]}\t{row["pure_price"]:.2f}')


def main():
    pm = PriceMachine()
    print(f'Загружено {pm.load_prices()} позиций товаров.')
    # pm.show_data() -- можно проверить, что загрузилось
    '''
        Логика работы программы
    '''
    while True:
        cmd = input().strip()

        if cmd.lower() == 'exit':
            break
        elif cmd == '':
            continue
        else:
            filtered_data = pm.find_text(text=cmd.lower())
            if filtered_data:
                pm.show_data(filtered_data)
                pm.export_to_html(data=filtered_data, file_name=f'output_by_{cmd}.html')
                print(f'По запросу "{cmd}" найдено {len(filtered_data)} позиций.')
            else:
                print(f'По Вашему запросу "{cmd}" ничего не нашлось.')

    pm.export_to_html(file_name='output_all_data.html')

if __name__ == '__main__':
    main()
    print('Работа завершена.')

import pandas as pd
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, NamedStyle

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime


class LeaseNumberParser:
    def __init__(self, lease_number):
        self.lease_number = lease_number

    def search_file(self) -> str:
        try:
            number_string = ''.join([x for x in self.lease_number if x.isdigit() or x == '0'])
            number = int(number_string)
            search_string = '*' + str(number) + '*'
        except ValueError:
            return 'Error'

        return search_string

    def search_tractstar(self) -> str:
        try:
            base_number = ''.join(self.lease_number.split(' ')[1:])
            number_string = ''.join([x for x in self.lease_number if x.isdigit() or x == '0'])
            alpha_string = ''.join([x for x in base_number if x.isalpha()])
            number = int(number_string)
            if alpha_string:
                search_string = str(number) + '-' + alpha_string
            else:
                search_string = str(number)
        except ValueError:
            return 'Error'

        return search_string

    def search_full(self) -> str:
        try:
            search = '*' + self.lease_number.replace('-', '*') + '*'
        except ValueError:
            return 'Error'
        return search

    def search_partial(self) -> str:
        try:
            search_split = self.lease_number.split('-')[:2]
            search = '*' + ('*'.join(search_split)) + '*'
        except ValueError:
            return 'Error'
        return search


class OrderProcessor(ABC):
    def __init__(self, order_form):
        self.order_form = order_form
        self.data = self.read_order_form()

    @abstractmethod
    def read_order_form(self):
        pass

    @abstractmethod
    def create_order_worksheet(self):
        pass

    @abstractmethod
    def process_data(self):
        pass

    @abstractmethod
    def create_folders(self):
        pass


class NMStateOrderProcessor(OrderProcessor):
    def read_order_form(self):
        return pd.read_excel(self.order_form)

    def process_data(self) -> pd.DataFrame:
        data = self.data

        data['Full Search'] = data['Lease'].apply(lambda x: LeaseNumberParser(x).search_full())
        data['Partial Search'] = data['Lease'].apply(lambda x: LeaseNumberParser(x).search_partial())

        blank_columns = pd.DataFrame(columns=['New Format', 'Tractstar', 'Old Format', 'MI Index', 'Documents', 'Basecamp'], index=data.index)
        data = pd.concat([data, blank_columns], axis=1)

        return data

    def create_order_worksheet(self):
        data = self.process_data()
        date_string = datetime.now().strftime("%Y%m%d")
        base_path = Path(self.order_form).absolute().parent
        file_name = f'{date_string}_nmstate_order_worksheet.xlsx'
        output_path = base_path / file_name
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        data.to_excel(writer, index=False, sheet_name='Worksheet')

        worksheet = writer.sheets['Worksheet']
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 9
        worksheet.column_dimensions['C'].width = 14
        worksheet.column_dimensions['D'].width = 14
        worksheet.column_dimensions['E'].width = 12
        worksheet.column_dimensions['F'].width = 12
        worksheet.column_dimensions['G'].width = 12
        worksheet.column_dimensions['H'].width = 12
        worksheet.column_dimensions['I'].width = 12
        worksheet.column_dimensions['J'].width = 30

        normal_style = NamedStyle(name="normal")
        normal_style.font = Font(name='Calibri', size=11)
        normal_style.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

        for row in worksheet.iter_rows(min_row=1, max_row=500):
            for cell in row:
                cell.style = normal_style
            worksheet.row_dimensions[row[0].row].height = None

        worksheet.freeze_panes = worksheet.cell(row=2, column=1)
        worksheet.auto_filter.ref = "A1:{}1".format(chr(ord('A') + data.shape[1] - 1))

        writer.close()

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = ['^Document Archive', '^MI Index', 'Runsheets']

        for lease in self.data['Lease Number']:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


class FederalOrderProcessor(OrderProcessor):
    def read_order_form(self):
        return pd.read_excel(self.order_form)

    def process_data(self) -> pd.DataFrame:
        data = self.data

        data['Files Search'] = data['Lease'].apply(lambda x: LeaseNumberParser(x).search_file())
        data['Tractstar Search'] = data['Lease'].apply(lambda x: LeaseNumberParser(x).search_tractstar())

        blank_columns = pd.DataFrame(columns=['New Format', 'Tractstar', 'Documents', 'Basecamp'], index=data.index)
        data = pd.concat([data, blank_columns], axis=1)

        return data

    def create_order_worksheet(self):
        data = self.process_data()
        date_string = datetime.now().strftime("%Y%m%d")
        base_path = Path(self.order_form).absolute().parent
        file_name = f'{date_string}_federal_order_worksheet.xlsx'
        output_path = base_path / file_name
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        data.to_excel(writer, index=False, sheet_name='Worksheet')

        worksheet = writer.sheets['Worksheet']
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 20
        worksheet.column_dimensions['C'].width = 14
        worksheet.column_dimensions['D'].width = 14
        worksheet.column_dimensions['E'].width = 12
        worksheet.column_dimensions['F'].width = 12
        worksheet.column_dimensions['G'].width = 12
        worksheet.column_dimensions['H'].width = 30

        normal_style = NamedStyle(name="normal")
        normal_style.font = Font(name='Calibri', size=11)
        normal_style.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

        for row in worksheet.iter_rows(min_row=1, max_row=500):
            for cell in row:
                cell.style = normal_style
            worksheet.row_dimensions[row[0].row].height = None

        worksheet.freeze_panes = worksheet.cell(row=2, column=1)
        worksheet.auto_filter.ref = "A1:{}1".format(chr(ord('A') + data.shape[1] - 1))

        writer.close()

    def create_folders(self):
        base_path = Path(self.order_form).absolute().parent
        directories = ['^Document Archive', 'Runsheets']

        for lease in self.data['Lease']:
            for directory in directories:
                (base_path / lease / directory).mkdir(exist_ok=True, parents=True)


if __name__ == '__main__':
    state_order_form_path = 'sample_data/order_state.xlsx'
    federal_order_form_path = 'sample_data/order_fed.xlsx'
    order_processor = NMStateOrderProcessor(state_order_form_path)
    # order_processor = FederalOrderProcessor(federal_order_form_path)
    order_processor.create_order_worksheet()




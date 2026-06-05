"""
FEC Parser services - Validation and parsing of FEC files.
Implements Article A47 A-1 of the French Tax Code (LPF).
"""
import csv
import io
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterator, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# FEC columns as per Article A47 A-1
FEC_COLUMNS = [
    ('JournalCode', str, True),
    ('JournalLib', str, True),
    ('EcritureNum', str, True),
    ('EcritureDate', 'date', True),
    ('CompteNum', str, True),
    ('CompteLib', str, True),
    ('CompAuxNum', str, False),
    ('CompAuxLib', str, False),
    ('PieceRef', str, True),
    ('PieceDate', 'date', True),
    ('EcritureLib', str, True),
    ('Debit', 'decimal', True),
    ('Credit', 'decimal', True),
    ('EcritureLet', str, False),
    ('DateLet', 'date', False),
    ('ValidDate', 'date', True),
    ('Montantdevise', 'decimal', False),
    ('Idevise', str, False),
]

REQUIRED_COLUMNS = [name for name, _, required in FEC_COLUMNS if required]


@dataclass
class FECValidationError:
    """Represents a validation error in a FEC file."""
    line_number: int
    column: str
    error_type: str
    message: str
    value: str = ""


@dataclass
class FECValidationResult:
    """Result of FEC file validation."""
    is_valid: bool
    errors: List[FECValidationError]
    row_count: int
    encoding: str
    separator: str
    columns_found: List[str]
    
    @property
    def error_count(self):
        return len(self.errors)


@dataclass
class FECRow:
    """Parsed FEC row."""
    line_number: int
    journal_code: str
    journal_lib: str
    ecriture_num: str
    ecriture_date: Optional[datetime]
    compte_num: str
    compte_lib: str
    comp_aux_num: str
    comp_aux_lib: str
    piece_ref: str
    piece_date: Optional[datetime]
    ecriture_lib: str
    debit: Decimal
    credit: Decimal
    ecriture_let: str
    date_let: Optional[datetime]
    valid_date: Optional[datetime]
    montant_devise: Optional[Decimal]
    idevise: str


class FECValidator:
    """
    Validates FEC files according to Article A47 A-1.
    """
    
    DATE_FORMATS = ['%Y%m%d', '%d/%m/%Y', '%Y-%m-%d']
    
    def __init__(self, max_errors: int = 100):
        self.max_errors = max_errors
    
    def detect_encoding(self, content: bytes) -> str:
        """Detect file encoding."""
        # Try UTF-8 first
        try:
            content.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass
        
        # Try ISO-8859-15 (French)
        try:
            content.decode('iso-8859-15')
            return 'iso-8859-15'
        except UnicodeDecodeError:
            pass
        
        # Fallback to latin-1
        return 'latin-1'
    
    def detect_separator(self, first_line: str) -> str:
        """Detect CSV separator (tab or pipe)."""
        if '\t' in first_line:
            return '\t'
        if '|' in first_line:
            return '|'
        if ';' in first_line:
            return ';'
        return '\t'  # Default
    
    def parse_date(self, value: str) -> Optional[datetime]:
        """Parse date with multiple format support."""
        if not value or value.strip() == '':
            return None
        
        value = value.strip()
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
    
    def parse_decimal(self, value: str) -> Decimal:
        """Parse decimal, handling French format (comma as separator)."""
        if not value or value.strip() == '':
            return Decimal('0')
        
        value = value.strip()
        # Replace comma with dot for French format
        value = value.replace(',', '.')
        # Remove spaces (thousand separators)
        value = value.replace(' ', '')
        
        try:
            return Decimal(value)
        except InvalidOperation:
            return Decimal('0')
    
    def validate(self, content: bytes) -> FECValidationResult:
        """
        Validate a FEC file content.
        
        Args:
            content: Raw bytes of the FEC file
            
        Returns:
            FECValidationResult with validation status and errors
        """
        errors: List[FECValidationError] = []
        
        # Detect encoding
        encoding = self.detect_encoding(content)
        text = content.decode(encoding)
        
        # Split into lines
        lines = text.splitlines()
        if not lines:
            errors.append(FECValidationError(
                line_number=0,
                column='',
                error_type='empty_file',
                message='Le fichier FEC est vide'
            ))
            return FECValidationResult(
                is_valid=False,
                errors=errors,
                row_count=0,
                encoding=encoding,
                separator='',
                columns_found=[]
            )
        
        # Detect separator from header
        separator = self.detect_separator(lines[0])
        
        # Parse header
        header = lines[0].split(separator)
        header = [col.strip().strip('"') for col in header]
        
        # Check required columns
        for required_col in REQUIRED_COLUMNS:
            if required_col not in header:
                errors.append(FECValidationError(
                    line_number=1,
                    column=required_col,
                    error_type='missing_column',
                    message=f'Colonne obligatoire manquante: {required_col}'
                ))
        
        if errors:
            return FECValidationResult(
                is_valid=False,
                errors=errors,
                row_count=0,
                encoding=encoding,
                separator=separator,
                columns_found=header
            )
        
        # Create column index map
        col_index = {name: i for i, name in enumerate(header)}
        
        # Validate data rows
        row_count = 0
        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue
                
            row_count += 1
            values = line.split(separator)
            values = [v.strip().strip('"') for v in values]
            
            # Check column count
            if len(values) != len(header):
                errors.append(FECValidationError(
                    line_number=line_num,
                    column='',
                    error_type='column_count',
                    message=f'Nombre de colonnes incorrect: {len(values)} au lieu de {len(header)}'
                ))
                if len(errors) >= self.max_errors:
                    break
                continue
            
            # Validate required fields
            for col_name, col_type, required in FEC_COLUMNS:
                if col_name not in col_index:
                    continue
                    
                value = values[col_index[col_name]]
                
                # Check required
                if required and not value:
                    errors.append(FECValidationError(
                        line_number=line_num,
                        column=col_name,
                        error_type='required_empty',
                        message=f'Champ obligatoire vide: {col_name}',
                        value=value
                    ))
                
                # Validate date format
                if col_type == 'date' and value:
                    if not self.parse_date(value):
                        errors.append(FECValidationError(
                            line_number=line_num,
                            column=col_name,
                            error_type='invalid_date',
                            message=f'Format de date invalide: {value}',
                            value=value
                        ))
                
                # Validate decimal format
                if col_type == 'decimal' and value:
                    try:
                        cleaned = value.replace(',', '.').replace(' ', '')
                        Decimal(cleaned)
                    except InvalidOperation:
                        errors.append(FECValidationError(
                            line_number=line_num,
                            column=col_name,
                            error_type='invalid_decimal',
                            message=f'Format numérique invalide: {value}',
                            value=value
                        ))
            
            if len(errors) >= self.max_errors:
                break
        
        return FECValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            row_count=row_count,
            encoding=encoding,
            separator=separator,
            columns_found=header
        )


class FECParser:
    """
    Streaming parser for FEC files.
    Parses in chunks to handle large files efficiently.
    """
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.validator = FECValidator()
    
    def parse_row(self, values: List[str], col_index: dict, line_number: int) -> FECRow:
        """Parse a single FEC row."""
        def get_val(col: str) -> str:
            idx = col_index.get(col)
            if idx is not None and idx < len(values):
                return values[idx]
            return ''
        
        return FECRow(
            line_number=line_number,
            journal_code=get_val('JournalCode'),
            journal_lib=get_val('JournalLib'),
            ecriture_num=get_val('EcritureNum'),
            ecriture_date=self.validator.parse_date(get_val('EcritureDate')),
            compte_num=get_val('CompteNum'),
            compte_lib=get_val('CompteLib'),
            comp_aux_num=get_val('CompAuxNum'),
            comp_aux_lib=get_val('CompAuxLib'),
            piece_ref=get_val('PieceRef'),
            piece_date=self.validator.parse_date(get_val('PieceDate')),
            ecriture_lib=get_val('EcritureLib'),
            debit=self.validator.parse_decimal(get_val('Debit')),
            credit=self.validator.parse_decimal(get_val('Credit')),
            ecriture_let=get_val('EcritureLet'),
            date_let=self.validator.parse_date(get_val('DateLet')),
            valid_date=self.validator.parse_date(get_val('ValidDate')),
            montant_devise=self.validator.parse_decimal(get_val('Montantdevise')) if get_val('Montantdevise') else None,
            idevise=get_val('Idevise'),
        )
    
    def parse_streaming(self, file_obj, encoding: str = None) -> Iterator[List[FECRow]]:
        """
        Parse FEC file in streaming chunks directly from a file object.
        Yields lists of FECRow objects, one chunk at a time.
        """
        if not encoding:
            sample = file_obj.read(1024 * 1024)
            encoding = self.validator.detect_encoding(sample)
            file_obj.seek(0)
            
        text_io = io.TextIOWrapper(file_obj, encoding=encoding, newline='')
        
        # Parse header
        first_line = text_io.readline()
        if not first_line:
            return
            
        separator = self.validator.detect_separator(first_line)
        header = first_line.split(separator)
        header = [col.strip().strip('"') for col in header]
        col_index = {name: i for i, name in enumerate(header)}
        
        chunk: List[FECRow] = []
        for line_num, line in enumerate(text_io, start=2):
            if not line.strip():
                continue
            
            values = line.split(separator)
            values = [v.strip().strip('"') for v in values]
            
            # Simple validation on the fly: skip malformed rows
            if len(values) == len(header):
                row = self.parse_row(values, col_index, line_num)
                chunk.append(row)
                
                if len(chunk) >= self.chunk_size:
                    yield chunk
                    chunk = []
        
        # Yield remaining
        if chunk:
            yield chunk
    
    def parse_all(self, file_obj) -> List[FECRow]:
        """Parse entire FEC file (for smaller files)."""
        rows = []
        for chunk in self.parse_streaming(file_obj):
            rows.extend(chunk)
        return rows

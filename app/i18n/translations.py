"""
Multi-language Translation System
Supports Arabic and English with RTL/LTR support
"""

import json
import os

class Translator:
    """Simple translation system for the ERP application"""
    
    def __init__(self, language='ar'):
        """
        Initialize translator
        
        Args:
            language: 'ar' for Arabic, 'en' for English
        """
        self.language = self.load_saved_language() or language
        self.translations = TRANSLATIONS
        self.config_file = 'language_config.json'
    
    def tr(self, key, **kwargs):
        """
        Translate a key to current language
        
        Args:
            key: Translation key (e.g., 'common.save')
            **kwargs: Format arguments for the translation string
        
        Returns:
            Translated string
        """
        keys = key.split('.')
        value = self.translations
        
        try:
            for k in keys:
                value = value[k]
            
            # Get translation for current language
            if isinstance(value, dict):
                translated = value.get(self.language, value.get('en', key))
            else:
                translated = value
            
            # Format with kwargs if provided
            if kwargs:
                translated = translated.format(**kwargs)
            
            return translated
        except (KeyError, TypeError):
            return key
    
    def set_language(self, language):
        """Change current language and save it"""
        if language in ['ar', 'en']:
            self.language = language
            self.save_language(language)
    
    def get_language(self):
        """Get current language"""
        return self.language
    
    def save_language(self, language):
        """Save language preference to file"""
        try:
            config = {'language': language}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving language: {e}")
    
    def load_saved_language(self):
        """Load saved language preference"""
        try:
            if os.path.exists('language_config.json'):
                with open('language_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('language', 'ar')
        except Exception as e:
            print(f"Error loading language: {e}")
        return 'ar'
    
    def is_rtl(self):
        """Check if current language is RTL"""
        return self.language == 'ar'


# Translation Dictionary
TRANSLATIONS = {
    # Common translations
    'common': {
        'save': {'ar': 'حفظ', 'en': 'Save'},
        'cancel': {'ar': 'إلغاء', 'en': 'Cancel'},
        'delete': {'ar': 'حذف', 'en': 'Delete'},
        'edit': {'ar': 'تعديل', 'en': 'Edit'},
        'add': {'ar': 'إضافة', 'en': 'Add'},
        'update': {'ar': 'تحديث', 'en': 'Update'},
        'search': {'ar': 'بحث', 'en': 'Search'},
        'clear': {'ar': 'مسح', 'en': 'Clear'},
        'close': {'ar': 'إغلاق', 'en': 'Close'},
        'new': {'ar': 'جديد', 'en': 'New'},
        'print': {'ar': 'طباعة', 'en': 'Print'},
        'export': {'ar': 'تصدير', 'en': 'Export'},
        'import': {'ar': 'استيراد', 'en': 'Import'},
        'refresh': {'ar': 'تحديث', 'en': 'Refresh'},
        'yes': {'ar': 'نعم', 'en': 'Yes'},
        'no': {'ar': 'لا', 'en': 'No'},
        'ok': {'ar': 'موافق', 'en': 'OK'},
        'confirm': {'ar': 'تأكيد', 'en': 'Confirm'},
        'success': {'ar': 'نجاح', 'en': 'Success'},
        'error': {'ar': 'خطأ', 'en': 'Error'},
        'warning': {'ar': 'تحذير', 'en': 'Warning'},
        'info': {'ar': 'معلومات', 'en': 'Information'},
        'loading': {'ar': 'جاري التحميل...', 'en': 'Loading...'},
        'coming_soon': {'ar': 'قريباً', 'en': 'Coming Soon'},
        'feature_coming_soon': {'ar': 'هذه الميزة قيد التطوير وستكون متاحة قريباً', 'en': 'This feature is under development and will be available soon'},
        'toolbar': {'ar': 'شريط الأدوات', 'en': 'Toolbar'},
        'ready': {'ar': 'جاهز', 'en': 'Ready'},
        'generate': {'ar': 'إنشاء', 'en': 'Generate'},
        'from_date': {'ar': 'من تاريخ', 'en': 'From Date'},
        'to_date': {'ar': 'إلى تاريخ', 'en': 'To Date'},
        'branch': {'ar': 'الفرع', 'en': 'Branch'},
        'currency': {'ar': 'العملة', 'en': 'Currency'},
        'payment_method': {'ar': 'طريقة الدفع', 'en': 'Payment Method'},
        'active': {'ar': 'نشط', 'en': 'Active'},
        'inactive': {'ar': 'غير نشط', 'en': 'Inactive'},
        'total': {'ar': 'الإجمالي', 'en': 'Total'},
        'subtotal': {'ar': 'المجموع الفرعي', 'en': 'Subtotal'},
        'discount': {'ar': 'خصم', 'en': 'Discount'},
        'tax': {'ar': 'ضريبة', 'en': 'Tax'},
        'date': {'ar': 'التاريخ', 'en': 'Date'},
        'time': {'ar': 'الوقت', 'en': 'Time'},
        'name': {'ar': 'الاسم', 'en': 'Name'},
        'code': {'ar': 'الرمز', 'en': 'Code'},
        'description': {'ar': 'الوصف', 'en': 'Description'},
        'status': {'ar': 'الحالة', 'en': 'Status'},
        'type': {'ar': 'النوع', 'en': 'Type'},
        'quantity': {'ar': 'الكمية', 'en': 'Quantity'},
        'price': {'ar': 'السعر', 'en': 'Price'},
        'amount': {'ar': 'المبلغ', 'en': 'Amount'},
        'actions': {'ar': 'الإجراءات', 'en': 'Actions'},
        'details': {'ar': 'التفاصيل', 'en': 'Details'},
        'select': {'ar': 'اختر', 'en': 'Select'},
        'all': {'ar': 'الكل', 'en': 'All'},
        'none': {'ar': 'لا شيء', 'en': 'None'},
        'filter': {'ar': 'تصفية', 'en': 'Filter'},
        'sort': {'ar': 'ترتيب', 'en': 'Sort'},
        'view': {'ar': 'عرض', 'en': 'View'},
        'download': {'ar': 'تحميل', 'en': 'Download'},
        'upload': {'ar': 'رفع', 'en': 'Upload'},
        'back': {'ar': 'رجوع', 'en': 'Back'},
        'next': {'ar': 'التالي', 'en': 'Next'},
        'previous': {'ar': 'السابق', 'en': 'Previous'},
        'first': {'ar': 'الأول', 'en': 'First'},
        'last': {'ar': 'الأخير', 'en': 'Last'},
        'page': {'ar': 'صفحة', 'en': 'Page'},
        'of': {'ar': 'من', 'en': 'of'},
        'to': {'ar': 'إلى', 'en': 'to'},
        'from': {'ar': 'من', 'en': 'from'},
        'id': {'ar': 'المعرف', 'en': 'ID'},
        'email': {'ar': 'البريد الإلكتروني', 'en': 'Email'},
        'phone': {'ar': 'الهاتف', 'en': 'Phone'},
        'address': {'ar': 'العنوان', 'en': 'Address'},
        'city': {'ar': 'المدينة', 'en': 'City'},
        'country': {'ar': 'الدولة', 'en': 'Country'},
        'notes': {'ar': 'ملاحظات', 'en': 'Notes'},
        'created': {'ar': 'تم الإنشاء', 'en': 'Created'},
        'updated': {'ar': 'تم التحديث', 'en': 'Updated'},
        'created_by': {'ar': 'أنشئ بواسطة', 'en': 'Created By'},
        'updated_by': {'ar': 'حدث بواسطة', 'en': 'Updated By'},
    },
    
    # Modules
    'modules': {
        'accounts': {'ar': 'الحسابات', 'en': 'Accounts'},
        'journals': {'ar': 'القيود اليومية', 'en': 'Journals'},
        'customers': {'ar': 'العملاء', 'en': 'Customers'},
        'suppliers': {'ar': 'الموردين', 'en': 'Suppliers'},
        'items': {'ar': 'الأصناف', 'en': 'Items'},
        'inventory': {'ar': 'المخزون', 'en': 'Inventory'},
        'sales': {'ar': 'المبيعات', 'en': 'Sales'},
        'purchases': {'ar': 'المشتريات', 'en': 'Purchases'},
        'pos': {'ar': 'نقاط البيع', 'en': 'POS'},
        'reports': {'ar': 'التقارير', 'en': 'Reports'},
        'settings': {'ar': 'الإعدادات', 'en': 'Settings'},
        'company': {'ar': 'الشركة', 'en': 'Company'},
        'branch': {'ar': 'الفرع', 'en': 'Branch'},
        'users': {'ar': 'المستخدمين', 'en': 'Users'},
        'roles': {'ar': 'الأدوار', 'en': 'Roles'},
        'permissions': {'ar': 'الصلاحيات', 'en': 'Permissions'},
        'cash_bank': {'ar': 'النقدية والبنوك', 'en': 'Cash & Bank'},
        'fixed_assets': {'ar': 'الأصول الثابتة', 'en': 'Fixed Assets'},
        'tax_compliance': {'ar': 'الامتثال الضريبي', 'en': 'Tax Compliance'},
        'iam': {'ar': 'إدارة الهوية والوصول', 'en': 'IAM'},
        'fiscal_periods': {'ar': 'الفترات المالية', 'en': 'Fiscal Periods'},
        'cost_centers': {'ar': 'مراكز التكلفة', 'en': 'Cost Centers'},
        'projects': {'ar': 'المشاريع', 'en': 'Projects'},
        'employees': {'ar': 'الموظفين', 'en': 'Employees'},
        'payroll': {'ar': 'الرواتب', 'en': 'Payroll'},
        'notifications': {'ar': 'الإشعارات', 'en': 'Notifications'},
        'workflows': {'ar': 'سير العمل', 'en': 'Workflows'},
        'general_config': {'ar': 'الإعدادات العامة', 'en': 'General Configuration'},
    },
    
    # Accounts Module
    'accounts': {
        'account_list': {'ar': 'قائمة الحسابات', 'en': 'Account List'},
        'account_details': {'ar': 'تفاصيل الحساب', 'en': 'Account Details'},
        'account_code': {'ar': 'رمز الحساب', 'en': 'Account Code'},
        'account_name_ar': {'ar': 'اسم الحساب (عربي)', 'en': 'Account Name (Arabic)'},
        'account_name_en': {'ar': 'اسم الحساب (إنجليزي)', 'en': 'Account Name (English)'},
        'account_type': {'ar': 'نوع الحساب', 'en': 'Account Type'},
        'parent_account': {'ar': 'الحساب الأب', 'en': 'Parent Account'},
        'level': {'ar': 'المستوى', 'en': 'Level'},
        'currency': {'ar': 'العملة', 'en': 'Currency'},
        'is_postable': {'ar': 'قابل للترحيل', 'en': 'Is Postable'},
        'asset': {'ar': 'أصل', 'en': 'Asset'},
        'liability': {'ar': 'التزام', 'en': 'Liability'},
        'equity': {'ar': 'حقوق ملكية', 'en': 'Equity'},
        'revenue': {'ar': 'إيراد', 'en': 'Revenue'},
        'expense': {'ar': 'مصروف', 'en': 'Expense'},
    },
    
    # Customers Module
    'customers': {
        'customer_list': {'ar': 'قائمة العملاء', 'en': 'Customer List'},
        'customer_details': {'ar': 'تفاصيل العميل', 'en': 'Customer Details'},
        'customer_name': {'ar': 'اسم العميل', 'en': 'Customer Name'},
        'customer_code': {'ar': 'رمز العميل', 'en': 'Customer Code'},
        'contact_person': {'ar': 'جهة الاتصال', 'en': 'Contact Person'},
        'credit_limit': {'ar': 'حد الائتمان', 'en': 'Credit Limit'},
        'balance': {'ar': 'الرصيد', 'en': 'Balance'},
    },
    
    # Suppliers Module
    'suppliers': {
        'supplier_list': {'ar': 'قائمة الموردين', 'en': 'Supplier List'},
        'supplier_details': {'ar': 'تفاصيل المورد', 'en': 'Supplier Details'},
        'supplier_name': {'ar': 'اسم المورد', 'en': 'Supplier Name'},
        'supplier_code': {'ar': 'رمز المورد', 'en': 'Supplier Code'},
        'payment_terms': {'ar': 'شروط الدفع', 'en': 'Payment Terms'},
    },
    
    # Company Module
    'company': {
        'company_list': {'ar': 'قائمة الشركات', 'en': 'Company List'},
        'company_details': {'ar': 'تفاصيل الشركة', 'en': 'Company Details'},
        'company_name': {'ar': 'اسم الشركة', 'en': 'Company Name'},
        'company_code': {'ar': 'رمز الشركة', 'en': 'Company Code'},
        'tax_number': {'ar': 'الرقم الضريبي', 'en': 'Tax Number'},
        'registration_number': {'ar': 'رقم السجل التجاري', 'en': 'Registration Number'},
    },
    
    # Branch Module
    'branch': {
        'branch_list': {'ar': 'قائمة الفروع', 'en': 'Branch List'},
        'branch_details': {'ar': 'تفاصيل الفرع', 'en': 'Branch Details'},
        'branch_name': {'ar': 'اسم الفرع', 'en': 'Branch Name'},
        'branch_code': {'ar': 'رمز الفرع', 'en': 'Branch Code'},
        'manager': {'ar': 'المدير', 'en': 'Manager'},
    },
    
    # Items Module
    'items': {
        'item_list': {'ar': 'قائمة الأصناف', 'en': 'Item List'},
        'item_details': {'ar': 'تفاصيل الصنف', 'en': 'Item Details'},
        'item_name': {'ar': 'اسم الصنف', 'en': 'Item Name'},
        'item_code': {'ar': 'رمز الصنف', 'en': 'Item Code'},
        'category': {'ar': 'الفئة', 'en': 'Category'},
        'unit': {'ar': 'الوحدة', 'en': 'Unit'},
        'cost_price': {'ar': 'سعر التكلفة', 'en': 'Cost Price'},
        'selling_price': {'ar': 'سعر البيع', 'en': 'Selling Price'},
        'stock_quantity': {'ar': 'الكمية المتوفرة', 'en': 'Stock Quantity'},
    },
    
    # Journals Module
    'journals': {
        'journal_list': {'ar': 'قائمة القيود', 'en': 'Journal List'},
        'journal_entry': {'ar': 'قيد يومية', 'en': 'Journal Entry'},
        'entry_number': {'ar': 'رقم القيد', 'en': 'Entry Number'},
        'entry_date': {'ar': 'تاريخ القيد', 'en': 'Entry Date'},
        'reference': {'ar': 'المرجع', 'en': 'Reference'},
        'debit': {'ar': 'مدين', 'en': 'Debit'},
        'credit': {'ar': 'دائن', 'en': 'Credit'},
        'balance': {'ar': 'الرصيد', 'en': 'Balance'},
        'draft': {'ar': 'مسودة', 'en': 'Draft'},
        'posted': {'ar': 'مرحل', 'en': 'Posted'},
        'reviewed': {'ar': 'مراجع', 'en': 'Reviewed'},
        'post': {'ar': 'ترحيل', 'en': 'Post'},
        'unpost': {'ar': 'إلغاء الترحيل', 'en': 'Unpost'},
        'lines': {'ar': 'السطور', 'en': 'Lines'},
        'add_line': {'ar': 'إضافة سطر', 'en': 'Add Line'},
        'remove_line': {'ar': 'حذف سطر', 'en': 'Remove Line'},
    },
    
    # Inventory Module
    'inventory': {
        'title': {'ar': 'إدارة المخزون', 'en': 'Inventory Management'},
        'stock_movements': {'ar': 'حركات المخزون', 'en': 'Stock Movements'},
        'stock_in': {'ar': 'إدخال', 'en': 'Stock In'},
        'stock_out': {'ar': 'إخراج', 'en': 'Stock Out'},
        'transfer': {'ar': 'تحويل', 'en': 'Transfer'},
        'adjustment': {'ar': 'تسوية', 'en': 'Adjustment'},
        'current_stock': {'ar': 'المخزون الحالي', 'en': 'Current Stock'},
        'reorder_level': {'ar': 'مستوى إعادة الطلب', 'en': 'Reorder Level'},
        'warehouse': {'ar': 'المستودع', 'en': 'Warehouse'},
        'stock_reports': {'ar': 'تقارير المخزون', 'en': 'Stock Reports'},
        'stock_transfer': {'ar': 'نقل المخزون', 'en': 'Stock Transfer'},
        'from_warehouse': {'ar': 'من مستودع', 'en': 'From Warehouse'},
        'to_warehouse': {'ar': 'إلى مستودع', 'en': 'To Warehouse'},
        'available_quantity': {'ar': 'الكمية المتاحة', 'en': 'Available Quantity'},
        'transfer_stock': {'ar': 'نقل المخزون', 'en': 'Transfer Stock'},
        'out_of_stock': {'ar': 'نفذ من المخزون', 'en': 'Out of Stock'},
        'low_stock': {'ar': 'مخزون منخفض', 'en': 'Low Stock'},
        'in_stock': {'ar': 'متوفر', 'en': 'In Stock'},
        'item_code': {'ar': 'رمز الصنف', 'en': 'Item Code'},
        'item_name': {'ar': 'اسم الصنف', 'en': 'Item Name'},
        'quantity': {'ar': 'الكمية', 'en': 'Quantity'},
        'unit': {'ar': 'الوحدة', 'en': 'Unit'},
        'cost_price': {'ar': 'سعر التكلفة', 'en': 'Cost Price'},
        'sale_price': {'ar': 'سعر البيع', 'en': 'Sale Price'},
        'total_value': {'ar': 'القيمة الإجمالية', 'en': 'Total Value'},
        'movement_type': {'ar': 'نوع الحركة', 'en': 'Movement Type'},
        'movement_date': {'ar': 'تاريخ الحركة', 'en': 'Movement Date'},
        'reference': {'ar': 'المرجع', 'en': 'Reference'},
        'notes': {'ar': 'ملاحظات', 'en': 'Notes'},
        'transfer_date': {'ar': 'تاريخ النقل', 'en': 'Transfer Date'},
        'transfer_quantity': {'ar': 'كمية النقل', 'en': 'Transfer Quantity'},
        'select_item': {'ar': 'اختر صنف', 'en': 'Select Item'},
        'select_warehouse': {'ar': 'اختر مستودع', 'en': 'Select Warehouse'},
        'stock_value_report': {'ar': 'تقرير قيمة المخزون', 'en': 'Stock Value Report'},
        'stock_movement_report': {'ar': 'تقرير حركة المخزون', 'en': 'Stock Movement Report'},
        'low_stock_report': {'ar': 'تقرير المخزون المنخفض', 'en': 'Low Stock Report'},
        'generate_report': {'ar': 'إنشاء التقرير', 'en': 'Generate Report'},
        'export_excel': {'ar': 'تصدير إلى Excel', 'en': 'Export to Excel'},
        'export_pdf': {'ar': 'تصدير إلى PDF', 'en': 'Export to PDF'},
        'print_report': {'ar': 'طباعة التقرير', 'en': 'Print Report'},
        'stock_summary': {'ar': 'ملخص المخزون', 'en': 'Stock Summary'},
        'stock_movements_report': {'ar': 'تقرير حركات المخزون', 'en': 'Stock Movements Report'},
        'low_stock_report': {'ar': 'تقرير المخزون المنخفض', 'en': 'Low Stock Report'},
        'stock_valuation': {'ar': 'تقييم المخزون', 'en': 'Stock Valuation'},
        'report_filters': {'ar': 'فلاتر التقرير', 'en': 'Report Filters'},
        'report_results': {'ar': 'نتائج التقرير', 'en': 'Report Results'},
        'stock_summary_report': {'ar': 'تقرير ملخص المخزون', 'en': 'Stock Summary Report'},
        'total_items': {'ar': 'إجمالي الأصناف', 'en': 'Total Items'},
        'low_stock_items': {'ar': 'أصناف المخزون المنخفض', 'en': 'Low Stock Items'},
        'total_movements': {'ar': 'إجمالي الحركات', 'en': 'Total Movements'},
        'total_in': {'ar': 'إجمالي الإدخال', 'en': 'Total In'},
        'total_out': {'ar': 'إجمالي الإخراج', 'en': 'Total Out'},
        'net_change': {'ar': 'صافي التغيير', 'en': 'Net Change'},
        'items_need_reorder': {'ar': 'أصناف تحتاج إعادة طلب', 'en': 'Items Need Reorder'},
        'stock_valuation_report': {'ar': 'تقرير تقييم المخزون', 'en': 'Stock Valuation Report'},
        'total_stock_value': {'ar': 'إجمالي قيمة المخزون', 'en': 'Total Stock Value'},
        'out_of_stock_items': {'ar': 'أصناف نفذت من المخزون', 'en': 'Out of Stock Items'},
        'edit_item': {'ar': 'تعديل الصنف', 'en': 'Edit Item'},
        'item_updated': {'ar': 'تم تحديث الصنف بنجاح', 'en': 'Item updated successfully'},
        'select_item_to_edit': {'ar': 'الرجاء اختيار صنف للتعديل', 'en': 'Please select an item to edit'},
    },
    
    # Financial Reports
    'reports': {
        'balance_sheet': {'ar': 'الميزانية العمومية', 'en': 'Balance Sheet'},
        'income_statement': {'ar': 'قائمة الدخل', 'en': 'Income Statement'},
        'cash_flow': {'ar': 'قائمة التدفقات النقدية', 'en': 'Cash Flow Statement'},
        'trial_balance': {'ar': 'ميزان المراجعة', 'en': 'Trial Balance'},
        'assets': {'ar': 'الأصول', 'en': 'Assets'},
        'liabilities': {'ar': 'الخصوم', 'en': 'Liabilities'},
        'equity': {'ar': 'حقوق الملكية', 'en': 'Equity'},
        'revenue': {'ar': 'الإيرادات', 'en': 'Revenue'},
        'expenses': {'ar': 'المصروفات', 'en': 'Expenses'},
        'net_income': {'ar': 'صافي الدخل', 'en': 'Net Income'},
        'gross_profit': {'ar': 'إجمالي الربح', 'en': 'Gross Profit'},
        'financial_reports': {'ar': 'التقارير المالية', 'en': 'Financial Reports'},
        'report_filters': {'ar': 'فلاتر التقرير', 'en': 'Report Filters'},
        'company': {'ar': 'الشركة', 'en': 'Company'},
        'branch': {'ar': 'الفرع', 'en': 'Branch'},
        'from_date': {'ar': 'من تاريخ', 'en': 'From Date'},
        'to_date': {'ar': 'إلى تاريخ', 'en': 'To Date'},
        'as_of_date': {'ar': 'حتى تاريخ', 'en': 'As of Date'},
        'generate_report': {'ar': 'إنشاء التقرير', 'en': 'Generate Report'},
        'select_company': {'ar': 'اختر الشركة', 'en': 'Select Company'},
        'select_branch': {'ar': 'اختر الفرع', 'en': 'Select Branch'},
        'all_branches': {'ar': 'جميع الفروع', 'en': 'All Branches'},
        'account_code': {'ar': 'رمز الحساب', 'en': 'Account Code'},
        'account_name': {'ar': 'اسم الحساب', 'en': 'Account Name'},
        'debit': {'ar': 'مدين', 'en': 'Debit'},
        'credit': {'ar': 'دائن', 'en': 'Credit'},
        'balance': {'ar': 'الرصيد', 'en': 'Balance'},
        'totals': {'ar': 'الإجماليات', 'en': 'TOTALS'},
        'balanced': {'ar': 'متوازن', 'en': 'BALANCED'},
        'out_of_balance': {'ar': 'غير متوازن', 'en': 'OUT OF BALANCE'},
        'total_assets': {'ar': 'إجمالي الأصول', 'en': 'Total Assets'},
        'total_liabilities': {'ar': 'إجمالي الخصوم', 'en': 'Total Liabilities'},
        'total_equity': {'ar': 'إجمالي حقوق الملكية', 'en': 'Total Equity'},
        'total_liabilities_equity': {'ar': 'إجمالي الخصوم وحقوق الملكية', 'en': 'Total Liabilities & Equity'},
        'total_revenue': {'ar': 'إجمالي الإيرادات', 'en': 'Total Revenue'},
        'total_expenses': {'ar': 'إجمالي المصروفات', 'en': 'Total Expenses'},
        'operating_activities': {'ar': 'الأنشطة التشغيلية', 'en': 'OPERATING ACTIVITIES'},
        'investing_activities': {'ar': 'الأنشطة الاستثمارية', 'en': 'INVESTING ACTIVITIES'},
        'financing_activities': {'ar': 'الأنشطة التمويلية', 'en': 'FINANCING ACTIVITIES'},
        'net_change_cash': {'ar': 'صافي التغير في النقد', 'en': 'Net Change in Cash'},
        'beginning_cash': {'ar': 'الرصيد النقدي الافتتاحي', 'en': 'Beginning Cash Balance'},
        'ending_cash': {'ar': 'الرصيد النقدي الختامي', 'en': 'Ending Cash Balance'},
    },
    
    # Messages
    'messages': {
        'save_success': {'ar': 'تم الحفظ بنجاح', 'en': 'Saved successfully'},
        'delete_success': {'ar': 'تم الحذف بنجاح', 'en': 'Deleted successfully'},
        'update_success': {'ar': 'تم التحديث بنجاح', 'en': 'Updated successfully'},
        'confirm_delete': {'ar': 'هل أنت متأكد من الحذف؟', 'en': 'Are you sure you want to delete?'},
        'required_field': {'ar': 'هذا الحقل مطلوب', 'en': 'This field is required'},
        'invalid_input': {'ar': 'إدخال غير صحيح', 'en': 'Invalid input'},
        'no_data': {'ar': 'لا توجد بيانات', 'en': 'No data available'},
        'please_select_company': {'ar': 'الرجاء اختيار شركة', 'en': 'Please select a company'},
        'no_tax_settings': {'ar': 'لا توجد إعدادات ضريبية للشركة المحددة', 'en': 'No tax settings found for the selected company'},
    },
    
    # Menu Items
    'menu': {
        'file': {'ar': 'ملف', 'en': 'File'},
        'edit': {'ar': 'تحرير', 'en': 'Edit'},
        'view': {'ar': 'عرض', 'en': 'View'},
        'tools': {'ar': 'أدوات', 'en': 'Tools'},
        'help': {'ar': 'مساعدة', 'en': 'Help'},
        'language': {'ar': 'اللغة', 'en': 'Language'},
        'arabic': {'ar': 'العربية', 'en': 'Arabic'},
        'english': {'ar': 'الإنجليزية', 'en': 'English'},
        'exit': {'ar': 'خروج', 'en': 'Exit'},
        'about': {'ar': 'حول', 'en': 'About'},
    },
    
    # Window Titles
    'windows': {
        'main_window': {'ar': 'Labeeb ERP - لبيب', 'en': 'Labeeb ERP'},
        'accounts': {'ar': 'إدارة الحسابات', 'en': 'Accounts Management'},
        'journals': {'ar': 'إدارة القيود اليومية', 'en': 'Journal Entries Management'},
        'customers': {'ar': 'إدارة العملاء', 'en': 'Customer Management'},
        'suppliers': {'ar': 'إدارة الموردين', 'en': 'Supplier Management'},
        'items': {'ar': 'إدارة الأصناف', 'en': 'Items Management'},
        'inventory': {'ar': 'إدارة المخزون', 'en': 'Inventory Management'},
        'sales_purchase': {'ar': 'إدارة المبيعات والمشتريات', 'en': 'Sales & Purchase Management'},
        'pos': {'ar': 'نقطة البيع', 'en': 'Point of Sale'},
        'reports': {'ar': 'التقارير', 'en': 'Reports'},
        'settings': {'ar': 'الإعدادات', 'en': 'Settings'},
    },
    
    # Settings
    'settings': {
        'language_settings': {'ar': 'إعدادات اللغة', 'en': 'Language Settings'},
        'select_language': {'ar': 'اختر اللغة', 'en': 'Select Language'},
        'current_settings': {'ar': 'الإعدادات الحالية', 'en': 'Current Settings'},
        'current_language': {'ar': 'اللغة الحالية', 'en': 'Current Language'},
        'layout_direction': {'ar': 'اتجاه التخطيط', 'en': 'Layout Direction'},
        'language_change_info': {
            'ar': 'ℹ️ ملاحظة: سيتم تطبيق تغيير اللغة فوراً. سيتم تغيير اتجاه الواجهة تلقائياً (RTL للعربية، LTR للإنجليزية).',
            'en': 'ℹ️ Note: Language change will be applied immediately. The interface direction will change automatically (RTL for Arabic, LTR for English).'
        },
        'rtl': {'ar': 'من اليمين إلى اليسار', 'en': 'Right to Left'},
        'ltr': {'ar': 'من اليسار إلى اليمين', 'en': 'Left to Right'},
        'general_settings': {'ar': 'الإعدادات العامة', 'en': 'General Settings'},
        'system_settings': {'ar': 'إعدادات النظام', 'en': 'System Settings'},
        'currency_settings': {'ar': 'إعدادات العملات', 'en': 'Currency Settings'},
        'payment_methods': {'ar': 'طرق الدفع', 'en': 'Payment Methods'},
        'loyalty_program': {'ar': 'برنامج الولاء', 'en': 'Loyalty Program'},
        'currency_name': {'ar': 'اسم العملة', 'en': 'Currency Name'},
        'currency_code': {'ar': 'رمز العملة', 'en': 'Currency Code'},
        'exchange_rate': {'ar': 'سعر الصرف', 'en': 'Exchange Rate'},
        'symbol': {'ar': 'الرمز', 'en': 'Symbol'},
        'payment_method_name': {'ar': 'اسم طريقة الدفع', 'en': 'Payment Method Name'},
        'is_default': {'ar': 'افتراضي', 'en': 'Is Default'},
        'program_name': {'ar': 'اسم البرنامج', 'en': 'Program Name'},
        'points_per_currency': {'ar': 'نقاط لكل وحدة عملة', 'en': 'Points Per Currency'},
        'min_points_redeem': {'ar': 'الحد الأدنى للاسترداد', 'en': 'Min Points to Redeem'},
    },
    
    # Sales & Purchase Module
    'sales': {
        'sales_invoices': {'ar': 'فواتير المبيعات', 'en': 'Sales Invoices'},
        'purchase_invoices': {'ar': 'فواتير المشتريات', 'en': 'Purchase Invoices'},
        'sales_orders': {'ar': 'أوامر المبيعات', 'en': 'Sales Orders'},
        'purchase_orders': {'ar': 'أوامر الشراء', 'en': 'Purchase Orders'},
        'invoice_no': {'ar': 'رقم الفاتورة', 'en': 'Invoice No'},
        'invoice_date': {'ar': 'تاريخ الفاتورة', 'en': 'Invoice Date'},
        'customer': {'ar': 'العميل', 'en': 'Customer'},
        'supplier': {'ar': 'المورد', 'en': 'Supplier'},
        'total_amount': {'ar': 'المبلغ الإجمالي', 'en': 'Total Amount'},
        'paid_amount': {'ar': 'المبلغ المدفوع', 'en': 'Paid Amount'},
        'remaining_amount': {'ar': 'المبلغ المتبقي', 'en': 'Remaining Amount'},
        'payment_status': {'ar': 'حالة الدفع', 'en': 'Payment Status'},
        'paid': {'ar': 'مدفوع', 'en': 'Paid'},
        'unpaid': {'ar': 'غير مدفوع', 'en': 'Unpaid'},
        'partial': {'ar': 'مدفوع جزئياً', 'en': 'Partially Paid'},
        'add_item': {'ar': 'إضافة صنف', 'en': 'Add Item'},
        'remove_item': {'ar': 'حذف صنف', 'en': 'Remove Item'},
        'item_name': {'ar': 'اسم الصنف', 'en': 'Item Name'},
        'quantity': {'ar': 'الكمية', 'en': 'Quantity'},
        'unit_price': {'ar': 'سعر الوحدة', 'en': 'Unit Price'},
        'discount': {'ar': 'الخصم', 'en': 'Discount'},
        'tax': {'ar': 'الضريبة', 'en': 'Tax'},
        'subtotal': {'ar': 'المجموع الفرعي', 'en': 'Subtotal'},
        'total': {'ar': 'الإجمالي', 'en': 'Total'},
        'notes': {'ar': 'ملاحظات', 'en': 'Notes'},
        'create_invoice': {'ar': 'إنشاء فاتورة', 'en': 'Create Invoice'},
        'edit_invoice': {'ar': 'تعديل فاتورة', 'en': 'Edit Invoice'},
        'delete_invoice': {'ar': 'حذف فاتورة', 'en': 'Delete Invoice'},
        'print_invoice': {'ar': 'طباعة فاتورة', 'en': 'Print Invoice'},
        'invoice_details': {'ar': 'تفاصيل الفاتورة', 'en': 'Invoice Details'},
        'invoice_items': {'ar': 'أصناف الفاتورة', 'en': 'Invoice Items'},
        'payment_info': {'ar': 'معلومات الدفع', 'en': 'Payment Information'},
        'order_no': {'ar': 'رقم الأمر', 'en': 'Order No'},
        'order_date': {'ar': 'تاريخ الأمر', 'en': 'Order Date'},
        'order_status': {'ar': 'حالة الأمر', 'en': 'Order Status'},
        'pending': {'ar': 'قيد الانتظار', 'en': 'Pending'},
        'approved': {'ar': 'معتمد', 'en': 'Approved'},
        'completed': {'ar': 'مكتمل', 'en': 'Completed'},
        'cancelled': {'ar': 'ملغي', 'en': 'Cancelled'},
        'convert_to_invoice': {'ar': 'تحويل لفاتورة', 'en': 'Convert to Invoice'},
        'search_invoices': {'ar': 'بحث في الفواتير', 'en': 'Search Invoices'},
        'filter_by_date': {'ar': 'تصفية حسب التاريخ', 'en': 'Filter by Date'},
        'filter_by_customer': {'ar': 'تصفية حسب العميل', 'en': 'Filter by Customer'},
        'filter_by_status': {'ar': 'تصفية حسب الحالة', 'en': 'Filter by Status'},
        'from_date': {'ar': 'من تاريخ', 'en': 'From Date'},
        'to_date': {'ar': 'إلى تاريخ', 'en': 'To Date'},
        'all_invoices': {'ar': 'جميع الفواتير', 'en': 'All Invoices'},
        'recent_invoices': {'ar': 'الفواتير الأخيرة', 'en': 'Recent Invoices'},
        'print_coming_soon': {'ar': 'ميزة الطباعة قيد التطوير وستكون متاحة قريباً', 'en': 'Print feature is under development and will be available soon'},
    },
}

# Global translator instance
_translator = Translator('ar')

def tr(key, **kwargs):
    """Global translation function"""
    return _translator.tr(key, **kwargs)

def set_language(language):
    """Set global language"""
    _translator.set_language(language)

def get_language():
    """Get current language"""
    return _translator.get_language()

"""
Labeeb ERP - Inventory Backend
Backend logic for inventory operations
"""

from PySide6.QtCore import QObject, Signal, Slot
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, or_
from decimal import Decimal
from datetime import datetime, date
from typing import List, Dict, Optional

from app.infrastructure.database import get_session
from app.infrastructure.repositories import (
    ItemRepository, StockMovementRepository, WarehouseRepository,
    UnitRepository
)
from app.domain.models import Item, StockMovement, Warehouse


class InventoryBackend(QObject):
    """Backend for inventory operations"""
    
    # Signals
    stock_movement_created = Signal(dict)
    stock_updated = Signal(dict)
    item_updated = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.services = {}
    
    def set_services(self, **services):
        """Set required services"""
        self.services = services
    
    # ==================== Stock Movements ====================
    
    @Slot(dict, result=bool)
    def create_stock_movement(self, movement_data: dict) -> bool:
        """Create a new stock movement"""
        try:
            with get_session() as db:
                stock_repo = StockMovementRepository(db)
                
                movement = StockMovement(
                    item_id=movement_data['item_id'],
                    movement_type=movement_data['movement_type'],
                    quantity=Decimal(str(movement_data['quantity'])),
                    cost=Decimal(str(movement_data.get('cost', 0))),
                    movement_date=movement_data['movement_date'],
                    ref_no=movement_data.get('ref_no'),
                    memo=movement_data.get('memo', ''),
                    company_id=movement_data.get('company_id', 1),
                    branch_id=movement_data.get('branch_id', 1),
                    warehouse_id=movement_data.get('warehouse_id'),
                    created_by=movement_data.get('user_id', 1)
                )
                
                created_movement = stock_repo.create_stock_movement(movement)
                db.commit()
                
                self.stock_movement_created.emit(self._format_stock_movement(created_movement))
                return True
                
        except Exception as e:
            print(f"Error creating stock movement: {e}")
            return False
    
    @Slot(result=list)
    def get_all_stock_movements(self) -> List[Dict]:
        """Get all stock movements"""
        try:
            with get_session() as db:
                movements = db.query(StockMovement).options(
                    joinedload(StockMovement.item)
                ).order_by(StockMovement.movement_date.desc()).all()
                
                return [self._format_stock_movement(m) for m in movements]
        except Exception as e:
            print(f"Error getting stock movements: {e}")
            return []
    
    @Slot(int, result=list)
    def get_stock_movements_by_item(self, item_id: int) -> List[Dict]:
        """Get stock movements for specific item"""
        try:
            with get_session() as db:
                movements = db.query(StockMovement).options(
                    joinedload(StockMovement.item)
                ).filter(StockMovement.item_id == item_id).order_by(
                    StockMovement.movement_date.desc()
                ).all()
                
                return [self._format_stock_movement(m) for m in movements]
        except Exception as e:
            print(f"Error getting stock movements: {e}")
            return []
    
    # ==================== Stock Levels ====================
    
    @Slot(int, result=dict)
    def get_item_stock_level(self, item_id: int) -> Dict:
        """Get current stock level for an item"""
        try:
            with get_session() as db:
                # Calculate stock from movements
                stock_in = db.query(func.sum(StockMovement.quantity)).filter(
                    StockMovement.item_id == item_id,
                    StockMovement.movement_type.in_([0, 2])  # In, Transfer In
                ).scalar() or 0
                
                stock_out = db.query(func.sum(StockMovement.quantity)).filter(
                    StockMovement.item_id == item_id,
                    StockMovement.movement_type.in_([1, 3])  # Out, Transfer Out
                ).scalar() or 0
                
                current_stock = float(stock_in) - float(stock_out)
                
                item = db.query(Item).filter(Item.id == item_id).first()
                
                return {
                    'item_id': item_id,
                    'item_name': item.name_ar if item else "Unknown",
                    'current_stock': current_stock,
                    'reorder_level': float(item.reorder_level) if item else 0,
                    'needs_reorder': current_stock <= float(item.reorder_level) if item else False
                }
        except Exception as e:
            print(f"Error getting stock level: {e}")
            return {}
    
    @Slot(result=list)
    def get_all_stock_levels(self) -> List[Dict]:
        """Get stock levels for all items"""
        try:
            with get_session() as db:
                items = db.query(Item).all()
                stock_levels = []
                
                for item in items:
                    stock_level = self.get_item_stock_level(item.id)
                    stock_levels.append(stock_level)
                
                return stock_levels
        except Exception as e:
            print(f"Error getting stock levels: {e}")
            return []
    
    @Slot(result=list)
    def get_low_stock_items(self) -> List[Dict]:
        """Get items with stock below reorder level"""
        try:
            stock_levels = self.get_all_stock_levels()
            return [s for s in stock_levels if s.get('needs_reorder', False)]
        except Exception as e:
            print(f"Error getting low stock items: {e}")
            return []
    
    # ==================== Stock Adjustments ====================
    
    @Slot(int, float, str, result=bool)
    def adjust_stock(self, item_id: int, quantity: float, reason: str) -> bool:
        """Adjust stock for an item"""
        try:
            movement_data = {
                'item_id': item_id,
                'movement_type': 3,  # Adjustment
                'quantity': abs(quantity),
                'movement_date': date.today(),
                'memo': f"Stock Adjustment: {reason}",
                'company_id': 1,
                'branch_id': 1
            }
            
            return self.create_stock_movement(movement_data)
        except Exception as e:
            print(f"Error adjusting stock: {e}")
            return False
    
    # ==================== Stock Transfer ====================
    
    @Slot(int, int, int, float, str, result=bool)
    def transfer_stock(self, item_id: int, from_warehouse: int, to_warehouse: int, 
                      quantity: float, notes: str) -> bool:
        """Transfer stock between warehouses"""
        try:
            with get_session() as db:
                stock_repo = StockMovementRepository(db)
                
                # Out from source warehouse
                movement_out = StockMovement(
                    item_id=item_id,
                    movement_type=3,  # Transfer Out
                    quantity=Decimal(str(quantity)),
                    movement_date=date.today(),
                    warehouse_id=from_warehouse,
                    memo=f"Transfer to Warehouse {to_warehouse}: {notes}",
                    company_id=1,
                    branch_id=1
                )
                stock_repo.create_stock_movement(movement_out)
                
                # In to destination warehouse
                movement_in = StockMovement(
                    item_id=item_id,
                    movement_type=2,  # Transfer In
                    quantity=Decimal(str(quantity)),
                    movement_date=date.today(),
                    warehouse_id=to_warehouse,
                    memo=f"Transfer from Warehouse {from_warehouse}: {notes}",
                    company_id=1,
                    branch_id=1
                )
                stock_repo.create_stock_movement(movement_in)
                
                db.commit()
                return True
                
        except Exception as e:
            print(f"Error transferring stock: {e}")
            return False
    
    # ==================== Helper Methods ====================
    
    def _format_stock_movement(self, movement: StockMovement) -> Dict:
        """Format stock movement for display"""
        if not movement:
            return {}
        
        movement_types = {
            0: "In",
            1: "Out",
            2: "Transfer In",
            3: "Transfer Out/Adjustment"
        }
        
        item_name = movement.item.name_ar if movement.item else "Unknown"
        
        return {
            'id': movement.id,
            'item_id': movement.item_id,
            'item_name': item_name,
            'movement_type': movement.movement_type,
            'movement_type_name': movement_types.get(movement.movement_type, "Unknown"),
            'quantity': float(movement.quantity),
            'cost': float(movement.cost),
            'movement_date': movement.movement_date.strftime('%Y-%m-%d'),
            'ref_no': movement.ref_no,
            'memo': movement.memo,
            'warehouse_id': movement.warehouse_id
        }
    
    @Slot(str, str, result=dict)
    def get_stock_report(self, from_date: str, to_date: str) -> Dict:
        """Get stock report for date range"""
        try:
            with get_session() as db:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
                
                movements = db.query(StockMovement).filter(
                    and_(
                        StockMovement.movement_date >= from_date_obj,
                        StockMovement.movement_date <= to_date_obj
                    )
                ).all()
                
                total_in = sum(m.quantity for m in movements if m.movement_type in [0, 2])
                total_out = sum(m.quantity for m in movements if m.movement_type in [1, 3])
                
                return {
                    'from_date': from_date,
                    'to_date': to_date,
                    'total_movements': len(movements),
                    'total_in': float(total_in),
                    'total_out': float(total_out),
                    'net_change': float(total_in - total_out)
                }
        except Exception as e:
            print(f"Error getting stock report: {e}")
            return {}

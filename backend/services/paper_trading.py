"""
Paper Trading Service
Virtual trading system with SQLite database
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

@dataclass
class Position:
    """Represents a position in the virtual portfolio"""
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    total_value: float

@dataclass
class Trade:
    """Represents a single trade"""
    id: int
    user_id: str
    symbol: str
    order_type: str
    quantity: float
    price: float
    total_amount: float
    timestamp: str
    status: str

@dataclass
class Portfolio:
    """Represents the entire virtual portfolio"""
    user_id: str
    cash_balance: float
    total_invested: float
    total_value: float
    total_pnl: float
    total_pnl_pct: float
    positions: List[Position]
    trades_count: int

class PaperTradingDB:
    """Database manager for paper trading"""

    def __init__(self, db_path: str = "data/paper_trading.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))

    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Users table - tracks virtual cash balance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                initial_balance REAL NOT NULL,
                current_balance REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Trades table - all buy/sell transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                total_amount REAL NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)

        # Positions table - current holdings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_entry_price REAL NOT NULL,
                total_cost REAL NOT NULL,
                opened_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, symbol)
            )
        """)

        # Signals table - trading signals history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                strategy TEXT NOT NULL,
                price REAL NOT NULL,
                indicator_values TEXT,
                timestamp TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def create_user(self, user_id: str, initial_balance: float = 1000000.0) -> bool:
        """Create a new user with initial cash balance"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO users (user_id, initial_balance, current_balance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, initial_balance, initial_balance, now, now))

            conn.commit()
            conn.close()
            logger.info(f"User {user_id} created with balance ${initial_balance:,.2f}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {user_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, initial_balance, current_balance, created_at, updated_at
            FROM users WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'user_id': row[0],
                'initial_balance': row[1],
                'current_balance': row[2],
                'created_at': row[3],
                'updated_at': row[4]
            }
        return None

    def execute_trade(
        self,
        user_id: str,
        symbol: str,
        order_type: OrderType,
        quantity: float,
        price: float
    ) -> Tuple[bool, str, Optional[int]]:
        """Execute a buy or sell trade"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get user balance
            cursor.execute("SELECT current_balance FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, "User not found", None

            current_balance = row[0]
            total_amount = quantity * price

            if order_type == OrderType.BUY:
                # Check if user has enough cash
                if current_balance < total_amount:
                    conn.close()
                    return False, f"Insufficient funds. Available: ${current_balance:,.2f}, Required: ${total_amount:,.2f}", None

                # Deduct cash
                new_balance = current_balance - total_amount

                # Update or create position
                cursor.execute("""
                    SELECT quantity, avg_entry_price, total_cost
                    FROM positions WHERE user_id = ? AND symbol = ?
                """, (user_id, symbol))

                position = cursor.fetchone()
                now = datetime.now().isoformat()

                if position:
                    # Update existing position
                    old_qty, old_avg, old_cost = position
                    new_qty = old_qty + quantity
                    new_cost = old_cost + total_amount
                    new_avg = new_cost / new_qty

                    cursor.execute("""
                        UPDATE positions
                        SET quantity = ?, avg_entry_price = ?, total_cost = ?, updated_at = ?
                        WHERE user_id = ? AND symbol = ?
                    """, (new_qty, new_avg, new_cost, now, user_id, symbol))
                else:
                    # Create new position
                    cursor.execute("""
                        INSERT INTO positions (user_id, symbol, quantity, avg_entry_price, total_cost, opened_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, symbol, quantity, price, total_amount, now, now))

            elif order_type == OrderType.SELL:
                # Check if user has enough shares
                cursor.execute("""
                    SELECT quantity FROM positions WHERE user_id = ? AND symbol = ?
                """, (user_id, symbol))

                position = cursor.fetchone()
                if not position or position[0] < quantity:
                    available = position[0] if position else 0
                    conn.close()
                    return False, f"Insufficient shares. Available: {available}, Required: {quantity}", None

                # Add cash from sale
                new_balance = current_balance + total_amount

                # Update position
                new_qty = position[0] - quantity
                now = datetime.now().isoformat()

                if new_qty == 0:
                    # Close position completely
                    cursor.execute("""
                        DELETE FROM positions WHERE user_id = ? AND symbol = ?
                    """, (user_id, symbol))
                else:
                    # Reduce position
                    cursor.execute("""
                        SELECT avg_entry_price, total_cost FROM positions
                        WHERE user_id = ? AND symbol = ?
                    """, (user_id, symbol))
                    avg_price, total_cost = cursor.fetchone()

                    new_cost = total_cost - (quantity * avg_price)

                    cursor.execute("""
                        UPDATE positions
                        SET quantity = ?, total_cost = ?, updated_at = ?
                        WHERE user_id = ? AND symbol = ?
                    """, (new_qty, new_cost, now, user_id, symbol))

            # Update user balance
            cursor.execute("""
                UPDATE users SET current_balance = ?, updated_at = ?
                WHERE user_id = ?
            """, (new_balance, datetime.now().isoformat(), user_id))

            # Record trade
            cursor.execute("""
                INSERT INTO trades (user_id, symbol, order_type, quantity, price, total_amount, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, symbol, order_type.value, quantity, price, total_amount,
                  datetime.now().isoformat(), OrderStatus.EXECUTED.value))

            trade_id = cursor.lastrowid

            conn.commit()
            conn.close()

            action = "Bought" if order_type == OrderType.BUY else "Sold"
            logger.info(f"{action} {quantity} shares of {symbol} at ${price:.2f} for user {user_id}")
            return True, f"{action} {quantity} shares at ${price:.2f}", trade_id

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False, f"Trade execution failed: {str(e)}", None

    def get_positions(self, user_id: str, current_prices: Dict[str, float]) -> List[Position]:
        """Get all positions for a user with current prices"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT symbol, quantity, avg_entry_price, total_cost
            FROM positions WHERE user_id = ?
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        positions = []
        for row in rows:
            symbol, quantity, avg_entry_price, total_cost = row
            current_price = current_prices.get(symbol, avg_entry_price)
            total_value = quantity * current_price
            unrealized_pnl = total_value - total_cost
            unrealized_pnl_pct = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0

            positions.append(Position(
                symbol=symbol,
                quantity=quantity,
                avg_entry_price=avg_entry_price,
                current_price=current_price,
                unrealized_pnl=round(unrealized_pnl, 2),
                unrealized_pnl_pct=round(unrealized_pnl_pct, 2),
                total_value=round(total_value, 2)
            ))

        return positions

    def get_portfolio(self, user_id: str, current_prices: Dict[str, float]) -> Optional[Portfolio]:
        """Get complete portfolio with all positions and performance"""
        user = self.get_user(user_id)
        if not user:
            return None

        positions = self.get_positions(user_id, current_prices)

        # Calculate totals
        total_invested = sum(p.quantity * p.avg_entry_price for p in positions)
        total_value = sum(p.total_value for p in positions)
        cash_balance = user['current_balance']
        total_portfolio_value = cash_balance + total_value

        # Calculate P&L
        total_pnl = total_value - total_invested
        initial_balance = user['initial_balance']
        total_account_pnl = total_portfolio_value - initial_balance
        total_pnl_pct = (total_account_pnl / initial_balance * 100) if initial_balance > 0 else 0

        # Count trades
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trades WHERE user_id = ?", (user_id,))
        trades_count = cursor.fetchone()[0]
        conn.close()

        return Portfolio(
            user_id=user_id,
            cash_balance=round(cash_balance, 2),
            total_invested=round(total_invested, 2),
            total_value=round(total_portfolio_value, 2),
            total_pnl=round(total_account_pnl, 2),
            total_pnl_pct=round(total_pnl_pct, 2),
            positions=positions,
            trades_count=trades_count
        )

    def get_trades_history(
        self,
        user_id: str,
        limit: int = 50,
        symbol: Optional[str] = None
    ) -> List[Trade]:
        """Get trade history for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if symbol:
            cursor.execute("""
                SELECT id, user_id, symbol, order_type, quantity, price, total_amount, timestamp, status
                FROM trades WHERE user_id = ? AND symbol = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (user_id, symbol, limit))
        else:
            cursor.execute("""
                SELECT id, user_id, symbol, order_type, quantity, price, total_amount, timestamp, status
                FROM trades WHERE user_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (user_id, limit))

        rows = cursor.fetchall()
        conn.close()

        trades = []
        for row in rows:
            trades.append(Trade(
                id=row[0],
                user_id=row[1],
                symbol=row[2],
                order_type=row[3],
                quantity=row[4],
                price=row[5],
                total_amount=row[6],
                timestamp=row[7],
                status=row[8]
            ))

        return trades

    def record_signal(
        self,
        symbol: str,
        signal_type: str,
        strategy: str,
        price: float,
        indicator_values: Optional[str] = None
    ) -> int:
        """Record a trading signal"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO signals (symbol, signal_type, strategy, price, indicator_values, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, signal_type, strategy, price, indicator_values, datetime.now().isoformat()))

        signal_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Recorded {signal_type} signal for {symbol} at ${price:.2f} using {strategy}")
        return signal_id

    def get_active_signals(self, symbol: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get recent active signals"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if symbol:
            cursor.execute("""
                SELECT id, symbol, signal_type, strategy, price, indicator_values, timestamp
                FROM signals WHERE symbol = ? AND is_active = 1
                ORDER BY timestamp DESC LIMIT ?
            """, (symbol, limit))
        else:
            cursor.execute("""
                SELECT id, symbol, signal_type, strategy, price, indicator_values, timestamp
                FROM signals WHERE is_active = 1
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        signals = []
        for row in rows:
            signals.append({
                'id': row[0],
                'symbol': row[1],
                'signal_type': row[2],
                'strategy': row[3],
                'price': row[4],
                'indicator_values': row[5],
                'timestamp': row[6]
            })

        return signals

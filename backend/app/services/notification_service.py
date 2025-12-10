# app/services/notification_service.py

from app.db import get_connection


def add_notification(user_id: int, message: str, ntype: str = "INFO"):
    """
    Add a notification for a user.
    ntype can be: 'INFO', 'ALERT', 'WARNING', etc.

    Returns: notification_id (int)
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        INSERT INTO notifications (user_id, message, type)
        VALUES (%s, %s, %s)
    """
    values = (user_id, message, ntype)

    try:
        cursor.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_notifications(user_id: int, include_read: bool = True):
    """
    Fetch notifications for a user.
    If include_read=False, only unread notifications are returned.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if include_read:
        sql = """
            SELECT notification_id, user_id, message, type,
                   created_at, is_read
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        cursor.execute(sql, (user_id,))
    else:
        sql = """
            SELECT notification_id, user_id, message, type,
                   created_at, is_read
            FROM notifications
            WHERE user_id = %s AND is_read = FALSE
            ORDER BY created_at DESC
        """
        cursor.execute(sql, (user_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def mark_notification_read(notification_id: int) -> bool:
    """
    Mark a single notification as read.
    Returns True if a row was updated, else False.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE notifications
        SET is_read = TRUE
        WHERE notification_id = %s
    """

    cursor.execute(sql, (notification_id,))
    conn.commit()

    updated = cursor.rowcount > 0

    cursor.close()
    conn.close()

    return updated


def mark_all_read(user_id: int) -> int:
    """
    Mark all notifications for a user as read.
    Returns the number of rows updated.
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
        UPDATE notifications
        SET is_read = TRUE
        WHERE user_id = %s AND is_read = FALSE
    """

    cursor.execute(sql, (user_id,))
    conn.commit()

    count = cursor.rowcount

    cursor.close()
    conn.close()

    return count

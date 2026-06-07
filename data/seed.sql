INSERT OR IGNORE INTO orders (
    order_id,
    customer_name,
    phone_tail,
    status,
    paid_at,
    shipped_at,
    carrier,
    tracking_no,
    refund_status,
    refund_requested_at,
    refund_amount,
    invoice_status
) VALUES
('SO202606001', '李先生', '1388', '已发货', '2026-06-04 09:20:00', '2026-06-05 11:30:00', '顺丰速运', 'SF123456789CN', '未申请', NULL, 0, '未开票'),
('SO202606002', '王女士', '6677', '未发货', '2026-06-05 20:15:00', NULL, NULL, NULL, '退款处理中', '2026-06-06 10:00:00', 299.00, '无需开票'),
('SO202606003', '张先生', '8866', '已签收', '2026-06-01 14:05:00', '2026-06-02 09:40:00', '京东物流', 'JD987654321CN', '退款成功', '2026-06-04 16:20:00', 199.00, '已开票');

INSERT OR IGNORE INTO order_items (id, order_id, product_name, sku, quantity, warranty_status) VALUES
(1, 'SO202606001', 'AirSound Pro 蓝牙耳机', 'ASP-BLACK', 1, '保修期内'),
(2, 'SO202606002', 'AirSound Lite 蓝牙耳机', 'ASL-WHITE', 1, '未发货'),
(3, 'SO202606003', 'AirSound Mini 蓝牙耳机', 'ASM-GREEN', 1, '保修期内');

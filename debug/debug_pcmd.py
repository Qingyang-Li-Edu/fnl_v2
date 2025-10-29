"""
V5 算法诊断工具 - 理解为什么 P_cmd = 100
"""

# 假设你的测试数据
负载数据 = 50  # kW
Buffer = 5     # kW
P_max = 100    # kW

# 算法计算过程
print("="*60)
print("V5 防逆流算法 - 计算过程诊断")
print("="*60)

print(f"\n【输入参数】")
print(f"  当前负载 L_t = {负载数据} kW")
print(f"  安全余量 Buffer = {Buffer} kW")
print(f"  逆变器最大功率 P_max = {P_max} kW")

print(f"\n【STUKF 预测】（假设）")
L_med = 负载数据  # 假设预测值 = 当前值
L_lb = 负载数据 - 2  # 假设置信下界稍低
print(f"  预测均值 L_med = {L_med} kW")
print(f"  置信下界 L_lb = {L_lb} kW")

print(f"\n【安全上界计算】")
U_A2 = max(0, L_lb - Buffer)
print(f"  概率性安全上界 U_A2 = L_lb - Buffer")
print(f"                      = {L_lb} - {Buffer}")
print(f"                      = {U_A2} kW")

print(f"\n【性能上界计算】")
U_B = max(0, L_med - Buffer)
print(f"  性能上界 U_B = L_med - Buffer")
print(f"              = {L_med} - {Buffer}")
print(f"              = {U_B} kW")

print(f"\n【物理约束】")
U = min(U_A2, P_max)
print(f"  实际上界 U = min(U_A2, P_max)")
print(f"             = min({U_A2}, {P_max})")
print(f"             = {U} kW")

print(f"\n【最终指令】")
P_cmd = min(U, P_max)
print(f"  PV限发指令 P_cmd = min(U, P_max)")
print(f"                   = min({U}, {P_max})")
print(f"                   = {P_cmd} kW")

print(f"\n{'='*60}")
print(f"【结论】")
print(f"{'='*60}")
print(f"  因为负载 ({负载数据} kW) > Buffer ({Buffer} kW)")
print(f"  所以安全上界 U_A2 = {U_A2} kW")
print(f"  由于 U_A2 ({U_A2}) > P_max ({P_max})")
print(f"  最终 P_cmd = P_max = {P_max} kW")
print(f"\n  这意味着：光伏可以全功率输出，不会造成逆流！")

print(f"\n{'='*60}")
print(f"【什么情况下 P_cmd < 100？】")
print(f"{'='*60}")
print(f"  需要满足：负载 < P_max + Buffer")
print(f"  例如：")
print(f"    - 如果负载 = 10 kW")
print(f"    - 那么 U_A2 ≈ 10 - 5 = 5 kW")
print(f"    - P_cmd = min(5, 100) = 5 kW  ← 需要限制！")
print(f"\n  即：当负载很小时，才会限制光伏输出")

print(f"\n{'='*60}")
print(f"【你的数据可能的问题】")
print(f"{'='*60}")
print(f"  1. 负载数据太大（> 100 kW）")
print(f"  2. P_max 设置太小（应该 > 实际最大负载）")
print(f"  3. Buffer 设置太小")
print(f"  4. 没有负载下降的场景")

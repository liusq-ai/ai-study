import sys

from services.customer_service import CustomerService


EXIT_COMMANDS = {"q", "quit", "exit", "退出"}


def print_answer(service: CustomerService, user_message: str) -> None:
    """输出一次 AI 客服处理结果。"""
    try:
        result = service.answer_message(user_message)
    except RuntimeError as error:
        print(f"错误：{error}")
        print()
        return
    except Exception as error:
        print(f"模型调用失败：{error}")
        print()
        return

    print(f"识别类型：{result['intent']['type']}")
    print(f"是否需要订单信息：{result['intent']['need_order_info']}")
    print(f"原因：{result['intent']['reason']}")
    print(f"客服回复：{result['reply']}")
    print()


def run_chat(service: CustomerService) -> None:
    """连续交互模式：用户可以反复输入问题。"""
    print("AI 客服已启动，输入 exit / quit / q / 退出 结束。")

    while True:
        user_message = input("用户：").strip()

        if not user_message:
            print("客服：请输入具体问题。")
            continue

        if user_message.lower() in EXIT_COMMANDS:
            print("客服：已结束会话。")
            return

        print_answer(service, user_message)


def run_main() -> None:
    """命令行入口：支持单次问答和连续交互。"""
    service = CustomerService()

    if len(sys.argv) == 1:
        run_chat(service)
        return

    user_message = sys.argv[1].strip()

    if not user_message:
        print("用户问题不能为空")
        return

    print(f"用户问题：{user_message}")
    print_answer(service, user_message)


if __name__ == "__main__":
    run_main()

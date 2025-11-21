#!/usr/bin/env python3
"""
雪球Cookie配置工具
用于手动配置和管理雪球网站的Cookie
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.manual_cookie import ManualCookieManager


def main():
    """主函数"""
    print("雪球Cookie配置工具")
    print("=" * 40)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看Cookie配置指南")
        print("2. 交互式配置Cookie")
        print("3. 检查当前Cookie状态")
        print("4. 恢复默认Cookie")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            ManualCookieManager.show_cookie_guide()
            
        elif choice == '2':
            success = ManualCookieManager.interactive_setup()
            if success:
                print("\n✅ Cookie配置完成！")
            else:
                print("\n❌ Cookie配置失败！")
                
        elif choice == '3':
            ManualCookieManager.check_cookie_status()
            
        elif choice == '4':
            confirm = input("确定要恢复默认Cookie吗？(y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                default_cookies = ManualCookieManager.get_default_cookies()
                if ManualCookieManager.save_cookies(default_cookies):
                    print("✅ 已恢复默认Cookie（游客模式）")
                else:
                    print("❌ 恢复默认Cookie失败")
            else:
                print("操作已取消")
                
        elif choice == '5':
            print("👋 再见！")
            break
            
        else:
            print("❌ 无效选项，请重新选择")


if __name__ == "__main__":
    main()
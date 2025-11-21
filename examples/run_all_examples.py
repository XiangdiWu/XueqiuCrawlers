"""
运行所有示例
"""
import sys
import os
import importlib
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_example(module_name, description):
    """运行单个示例"""
    print(f"\n{'='*60}")
    print(f"运行示例: {description}")
    print(f"模块: {module_name}")
    print(f"{'='*60}")
    
    try:
        # 动态导入模块
        module = importlib.import_module(module_name)
        
        # 运行main函数
        if hasattr(module, 'main'):
            module.main()
            print(f"✓ {description} 运行成功")
            return True
        else:
            print(f"⚠ {module_name} 没有main函数")
            return False
            
    except Exception as e:
        print(f"✗ {description} 运行失败: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("雪球股票数据爬虫 - 运行所有示例")
    print("=" * 60)
    
    # 示例列表
    examples = [
        ("examples.basic_usage", "基础使用示例"),
        ("examples.individual_crawlers", "单独爬虫使用示例"),
        ("examples.database_operations", "数据库操作示例"),
        ("examples.custom_crawler", "自定义爬虫示例"),
        ("examples.configuration_example", "配置使用示例"),
        ("examples.error_handling", "错误处理示例"),
        ("examples.batch_processing", "批处理示例"),
        ("examples.testing_example", "测试示例"),
        ("examples.advanced_usage", "高级使用示例"),
    ]
    
    # 运行结果统计
    results = {
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    # 逐个运行示例
    for module_name, description in examples:
        success = run_example(module_name, description)
        results['details'].append({
            'module': module_name,
            'description': description,
            'success': success
        })
        
        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
        
        # 询问是否继续
        if not success:
            try:
                response = input("是否继续运行下一个示例？(y/n): ").lower()
                if response != 'y':
                    break
            except KeyboardInterrupt:
                print("\n用户中断")
                break
    
    # 显示总结
    print(f"\n{'='*60}")
    print("运行总结")
    print(f"{'='*60}")
    print(f"总计: {len(examples)} 个示例")
    print(f"成功: {results['success']} 个")
    print(f"失败: {results['failed']} 个")
    print(f"成功率: {results['success']/len(examples):.1%}")
    
    print("\n详细结果:")
    for detail in results['details']:
        status = "✓" if detail['success'] else "✗"
        print(f"  {status} {detail['description']}")
    
    print(f"\n{'='*60}")
    if results['failed'] == 0:
        print("🎉 所有示例都运行成功！")
    else:
        print(f"⚠ 有 {results['failed']} 个示例运行失败，请检查错误信息")
    
    return results['failed'] == 0


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
        sys.exit(1)
    except Exception as e:
        print(f"\n运行过程中发生未预期的错误: {e}")
        traceback.print_exc()
        sys.exit(1)
/**
 * 雪球反混淆JavaScript代码
 * 用于生成acw_sc__v2等反爬参数
 */

// 反混淆工具函数
const Deobfuscator = {
    // 基础解密函数
    decrypt: function(encryptedStr, key = 'xueqiu') {
        try {
            const crypto = require('crypto');
            const decipher = crypto.createDecipher('aes-256-cbc', key);
            let decrypted = decipher.update(encryptedStr, 'hex', 'utf8');
            decrypted += decipher.final('utf8');
            return decrypted;
        } catch (e) {
            return encryptedStr;
        }
    },
    
    // 生成时间戳
    getTimestamp: function() {
        return Date.now();
    },
    
    // 生成随机数
    getRandom: function(min = 100000, max = 999999) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },
    
    // MD5哈希
    md5: function(str) {
        const crypto = require('crypto');
        return crypto.createHash('md5').update(str).digest('hex');
    },
    
    // Base64编码
    base64Encode: function(str) {
        return Buffer.from(str).toString('base64');
    }
};

// 雪球Cookie生成器
const XueqiuCookieGenerator = {
    // 生成ACW-TC
    generateACWTC: function() {
        const timestamp = Deobfuscator.getTimestamp();
        const random = Deobfuscator.getRandom();
        const data = `${timestamp}_${random}`;
        const hash = Deobfuscator.md5(data + 'acw_tc');
        return Deobfuscator.base64Encode(`${timestamp}_${hash.substring(0, 8)}`);
    },
    
    // 生成ACWSCVI (acw_sc__v2)
    generateACWSCVI: function() {
        const timestamp = Deobfuscator.getTimestamp();
        const random = Deobfuscator.getRandom();
        
        // 模拟雪球的复杂生成逻辑
        const step1 = timestamp.toString().split('').reverse().join('');
        const step2 = random.toString().padStart(6, '0');
        const step3 = 'xueqiu_anti_crawler';
        
        const combined = step1 + step2 + step3;
        const hash = Deobfuscator.md5(combined);
        
        // 更复杂的编码逻辑
        const encoded = Deobfuscator.base64Encode(`${timestamp}_${hash.substring(0, 16)}_${random}`);
        
        return encoded;
    },
    
    // 生成完整的Cookie集合
    generateAllCookies: function() {
        return {
            'ACW-TC': this.generateACWTC(),
            'ACWSCVI': this.generateACWSCVI(),
            'timestamp': Deobfuscator.getTimestamp()
        };
    }
};

// 模拟雪球的reload函数（反混淆版本）
function reload(arg2) {
    try {
        // 解析传入的参数
        const params = typeof arg2 === 'string' ? JSON.parse(arg2) : arg2;
        
        // 生成新的Cookie值
        const cookies = XueqiuCookieGenerator.generateAllCookies();
        
        // 模拟设置Cookie的逻辑
        const result = {
            success: true,
            cookies: cookies,
            timestamp: cookies.timestamp
        };
        
        return result;
    } catch (e) {
        return {
            success: false,
            error: e.message
        };
    }
}

// 高级反混淆函数
function advancedDeobfuscation(obfuscatedCode) {
    try {
        // 移除注释和空白
        let deobfuscated = obfuscatedCode
            .replace(/\/\*[\s\S]*?\*\//g, '')
            .replace(/\/\/.*$/gm, '')
            .replace(/\s+/g, ' ')
            .trim();
        
        // 替换常见的混淆模式
        deobfuscated = deobfuscated
            .replace(/\\x([0-9a-fA-F]{2})/g, (match, hex) => String.fromCharCode(parseInt(hex, 16)))
            .replace(/\\u([0-9a-fA-F]{4})/g, (match, unicode) => String.fromCharCode(parseInt(unicode, 16)))
            .replace(/\\([0-7]{1,3})/g, (match, octal) => String.fromCharCode(parseInt(octal, 8)));
        
        // 处理变量名混淆（简单示例）
        const varMap = {};
        let varCounter = 0;
        
        deobfuscated = deobfuscated.replace(/_0x[a-f0-9]+/g, (match) => {
            if (!varMap[match]) {
                varMap[match] = `var_${varCounter++}`;
            }
            return varMap[match];
        });
        
        return deobfuscated;
    } catch (e) {
        console.error('反混淆失败:', e.message);
        return obfuscatedCode;
    }
}

// 主执行函数
function main() {
    try {
        console.log('=== 雪球反混淆工具 ===');
        
        // 生成Cookie
        const cookies = XueqiuCookieGenerator.generateAllCookies();
        
        console.log('生成的Cookie:');
        Object.keys(cookies).forEach(key => {
            console.log(`${key}: ${cookies[key]}`);
        });
        
        // 测试reload函数
        const testArg2 = {
            url: 'https://xueqiu.com',
            timestamp: Date.now()
        };
        
        const reloadResult = reload(JSON.stringify(testArg2));
        console.log('\nReload函数测试结果:', JSON.stringify(reloadResult, null, 2));
        
        return cookies;
        
    } catch (e) {
        console.error('执行失败:', e.message);
        return null;
    }
}

// 如果直接运行此脚本
if (require.main === module) {
    main();
}

// 导出函数供其他模块使用
module.exports = {
    Deobfuscator,
    XueqiuCookieGenerator,
    reload,
    advancedDeobfuscation,
    main
};
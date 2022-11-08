const NodePolyfillPlugin = require('node-polyfill-webpack-plugin');

module.exports = {
    
    configureWebpack: {
        plugins: [
            new NodePolyfillPlugin()
        ]
    },
    pluginOptions: {
        electronBuilder: {
            preload: './src/preload.js',
            
            // Or, for multiple preload files:
            // preload: { preload: 'src/preload.js', otherPreload: 'src/preload2.js' }
            builderOptions: {
                appId: 'com.linerai.liner',
                afterSign: "./afterSignHook.js",
                "extraResources": [{
                    "from": process.env.BACKEND_BUILD_PATH , 
                    "to": "core",
                    "filter": [
                        "**/*"
                    ]
                }], // access via path.join(path.dirname(__dirname), 'liner_core' );

                "mac": {
                    "icon" : "build/Icon-1024.png" , 
                    "hardenedRuntime": true,
                    "entitlements": "build/entitlements.mac.plist",
                    "entitlementsInherit": "build/entitlements.mac.plist",
                    "minimumSystemVersion": "12.3.0",
                    "extendInfo": {
                        "LSMinimumSystemVersion": "12.3.0"
                    } , 
                    
                    "target": {
                        "target": "dmg",
                        "arch": [
                            process.env.BUILD_ARCH  //'arm64' , 'x64'
                        ]
                    }
                },

                "win": {
                    "icon" : "build/Icon-1024.png" , 
                    "target": {
                        "target": "NSIS",
                        "arch": [
                            process.arch   
                        ]
                    }
                }
            }


        }
    }
}
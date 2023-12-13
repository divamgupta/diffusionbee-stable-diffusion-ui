try {
    var build_config = require('./build_config.json');
    console.log(build_config + "\n\n\n\n\n")
} catch (err) {
    var build_config = {}
}


module.exports = {
    
    pluginOptions: {
        electronBuilder: {
            preload: './src/preload.js',
            
            // Or, for multiple preload files:
            // preload: { preload: 'src/preload.js', otherPreload: 'src/preload2.js' }
            builderOptions: {
                appId: 'com.diffusionbee.diffusionbee',
                artifactName: "DiffusionBee"+(build_config.build_name||"")+"-${version}.${ext}",

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
                    "minimumSystemVersion": build_config.min_os_version || "12.6.0",
                    "extendInfo": {
                        "LSMinimumSystemVersion": build_config.min_os_version || "12.6.0"
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
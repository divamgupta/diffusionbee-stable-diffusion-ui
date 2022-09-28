
function compute_n_cols() {
    let w = window.innerWidth;
    let n_col;
    if (w < 576) { n_col = 2 } else if (w < 668) { n_col = 3 } else if (w < 892) { n_col = 4 } else if (w < 1100) { n_col = 5 } else if (w < 1600) { n_col = 6 } else if (w < 1900) { n_col = 7 } else if (w < 2100) { n_col = 8 } else if (w < 2400) { n_col = 9 }

    n_col -= 1;
    return n_col;
}



function simple_hash( strr ) {
    var hash = 0;
    for (var i = 0; i < strr.length; i++) {
        var char = strr.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}


function resolve_asset_illustration(name) {
    let pre_assets_list_svg = [
      ];
    let pre_assets_list_png = [
        ];
    if (pre_assets_list_svg.includes(name))
        return require("@/assets/" + name + ".svg")
    else  if (pre_assets_list_png.includes(name))
        return require("@/assets/" + name + ".png")
    else if (name.startsWith("https://") || name.startsWith("http://"))
        return name;
    else
        return "file://" + name;
}




const escapeHtml = (unsafe) => {
    return unsafe.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');
}


function open_popup( img_url , text ){
            
    let css = `
        <style>
        img {
    
                     width: 100%;
                      height:100%;
                      object-fit: contain;
                      user-drag: none;
          
            }
            @media (prefers-color-scheme: light) {
                body {
                    background-color: #f2f2f2;
                }
            }
            @media (prefers-color-scheme: dark) {
                body {
                    background-color: #303030;
                }
            }
            body{
                padding : 0;
                margin: 0;
                -webkit-user-select: none;
                    -webkit-app-region: drag;
                  
                      user-drag: none;
                        -webkit-user-drag: none;
                        user-select: none;
                        -moz-user-select: none;
                        -webkit-user-select: none;
                        -ms-user-select: none;
            }
            p{
                padding:40px;
            }
            audio{
                position: fixed ; 
                bottom: 20px;
               left: 50%;
                transform: translateX(-50%);
            }
       </style>
    `
    let html = '<html><head>'+css+'</head><body>' ;

    if (img_url)
        html += '<img src="'+escapeHtml(img_url)+'"> ';
    
    if( text )
         html += '<p> '+ escapeHtml(text) +' </p>';
    
    html += '</body></html>'
    let uri = "data:text/html," + encodeURIComponent(html);
    window.open(uri, '_blank', 'top=100,left=100,frame=false,nodeIntegration=no');
    

}




export { compute_n_cols ,resolve_asset_illustration , simple_hash , open_popup}
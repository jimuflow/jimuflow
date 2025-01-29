(function () {
    if (window.__post_init_js_injected__) {
        return
    }
    window.__iframe_id__ = new Date().getTime().toString(36) + '_' + Math.random().toString(36).substring(2, 9);
    if (window.parent!==window.self) {
        window.parent.postMessage({
            type: '__post_init_js_injected__',
            data: window.__iframe_id__
        }, '*');
    }

    function init() {

        function injectStyle(){
            const styleId='18e0a9a2-b4ca-4ff8-b4d2-ad2bc1fe3ce4'
            if(document.getElementById(styleId)){
                return
            }
            const cssContent = '.qt-highlight-hover {box-shadow: 0 0 10px rgba(255, 165, 0, 0.8) !important;}.qt-highlight-selected,.qt-highlight-source {box-shadow: 0 0 10px rgba(0, 121, 54, 0.8) !important;}.qt-highlight-target {box-shadow: 0 0 10px rgba(255, 73, 73, 0.8) !important;}'
            const style = document.createElement('style');
            style.type = 'text/css';
            style.appendChild(document.createTextNode(cssContent));
            style.id=styleId
            document.head.appendChild(style);
        }

        injectStyle()

        document.body.addEventListener('mouseover', (event) => {
            injectStyle()
            if (event.target !== document.body) {
                event.target.classList.add('qt-highlight-hover');
            }
        }, true);
        document.body.addEventListener('mouseout', (event) => {
            event.target.classList.remove('qt-highlight-hover');
        }, true);
    }

    if (document.readyState === "loading") {
        // 此时加载尚未完成
        document.addEventListener("DOMContentLoaded", init);
    } else {
        // `DOMContentLoaded` 已经被触发
        init();
    }
    window.__post_init_js_injected__ = true
})()


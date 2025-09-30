# Moonshot Tool-Use Documentation (fetched)

Source: https://platform.moonshot.ai/docs/api/tool-use

Raw fetch (truncated/JS payload present):

<raw>
.data-ant-cssinjs-cache-path{content:"";}!function(){try{var d=document.documentElement,c=d.classList;c.remove('light','dark');var e=localStorage.getItem('moonshot-theme');if('system'===e||(!e&&false)){var t='(prefers-color-scheme: dark)',m=window.matchMedia(t);if(m.media!==t||m.matches){d.style.colorScheme = 'dark';c.add('dark')}else{d.style.colorScheme = 'light';c.add('light')}}else if(e){c.add(e|| '')}else{c.add('light')}if(e==='light'||e==='dark'||!e)d.style.colorScheme=e||'light'}catch(e){}}(){"props":{"pageProps":{}},"page":"/docs/api/tool-use.en-US","query":{},"buildId":"1pLLaUvl9K--22uR8OVJF","nextExport":true,"autoExport":true,"isFallback":false,"locale":"en-US","locales":["en-US","zh-CN"],"defaultLocale":"en-US","scriptLoader":[]}
</raw>

Note:
- The docs site returns a Next.js bootstrap payload; specific schema sections require browser rendering. For API compliance we matched against the live provider error and OpenAI-compatible expectations.


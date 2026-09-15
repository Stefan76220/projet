(function(){try{if(typeof document<`u`){var e=document.createElement(`style`);e.setAttribute(`id`,`canvas-editor-style`),e.appendChild(document.createTextNode(`.ce-select-control-popup{z-index:1;box-sizing:border-box;background-color:#fff;border:1px solid #e4e7ed;border-radius:4px;min-width:69px;max-width:160px;max-height:225px;margin:5px 0;position:absolute;overflow-y:auto;box-shadow:0 2px 12px #0000001a}.ce-select-control-popup ul{box-sizing:border-box;margin:0;padding:3px 0;list-style:none}.ce-select-control-popup ul li{white-space:nowrap;text-overflow:ellipsis;color:#666;box-sizing:border-box;cursor:pointer;height:36px;padding:0 20px;font-size:13px;line-height:36px;position:relative;overflow:hidden}.ce-select-control-popup ul li:hover{background-color:#eef2fd}.ce-select-control-popup ul li.active{color:var(--COLOR-HOVER,#5175f4);font-weight:700}.ce-calculator{z-index:1;box-sizing:border-box;background-color:#fff;border:1px solid #e4e7ed;border-radius:4px;width:200px;margin:5px 0;padding:8px;position:absolute;box-shadow:0 2px 12px #0000001a}.ce-calculator-display{text-align:right;box-sizing:border-box;text-overflow:ellipsis;background-color:#f5f7fa;border:1px solid #e4e7ed;border-radius:4px;width:100%;height:40px;margin-bottom:8px;padding:0 10px;font-size:16px;line-height:40px;overflow:hidden}.ce-calculator-buttons{grid-template-columns:repeat(4,1fr);gap:4px;display:grid}.ce-calculator-button{cursor:pointer;box-sizing:border-box;background-color:#fff;border:1px solid #e4e7ed;border-radius:4px;width:100%;height:36px;font-size:14px;transition:all .2s}.ce-calculator-button:hover{background-color:#eef2fd;border-color:#c6d1ff}.ce-calculator-button:active{background-color:#e1e8ff}.ce-calculator-button.operator{background-color:#f5f7fa}.ce-calculator-button.operator:hover{background-color:#eef2fd}.ce-calculator-button.equal{background-color:var(--COLOR-HOVER,#5175f4);color:#fff;border-color:var(--COLOR-HOVER,#5175f4)}.ce-calculator-button.equal:hover{background-color:var(--COLOR-HOVER,#6a84ff);border-color:var(--COLOR-HOVER,#6a84ff)}.ce-calculator-button.utility{background-color:#f0f2f5}.ce-calculator-button.utility:hover{background-color:#e6e8eb}.ce-date-container{z-index:1;color:#606266;-webkit-user-select:none;user-select:none;background:#fff;border:1px solid #e4e7ed;border-radius:4px;width:300px;padding:10px;display:none;position:absolute;left:0;right:0;overflow:hidden;box-shadow:0 2px 12px #0000001a}.ce-date-container.active{display:block}.ce-date-wrap{display:none}.ce-date-wrap.active{display:block}.ce-date-wrap.year-mode .ce-date-week,.ce-date-wrap.year-mode .ce-date-day,.ce-date-wrap.month-mode .ce-date-week,.ce-date-wrap.month-mode .ce-date-day{display:none}.ce-date-title{text-align:center;color:#606266;justify-content:center;align-items:center;font-size:16px;display:flex}.ce-date-title>span{display:inline-block}.ce-date-title>span:not(.ce-date-title__now){cursor:pointer;font-family:cursive}.ce-date-title>span:not(.ce-date-title__now):hover{color:#5175f4}.ce-date-title .ce-date-title__pre-year,.ce-date-title .ce-date-title__pre-month{width:15%}.ce-date-title .ce-date-title__now{width:40%}.ce-date-title .ce-date-title__year-label,.ce-date-title .ce-date-title__month-label{cursor:pointer;white-space:nowrap}.ce-date-title .ce-date-title__year-label:hover,.ce-date-title .ce-date-title__month-label:hover{color:#5175f4}.ce-date-title .ce-date-title__next-year,.ce-date-title .ce-date-title__next-month{width:15%}.ce-date-week{border-bottom:1px solid #e4e7ed;justify-content:center;width:100%;margin-top:15px;padding-bottom:5px;display:flex}.ce-date-week>span{text-align:center;color:#606266;width:14.2857%;font-size:14px;list-style:none}.ce-date-day{flex-wrap:wrap;align-items:center;width:100%;margin-top:5px;display:flex}.ce-date-day>div{text-align:center;color:#606266;cursor:pointer;border-radius:4px;width:14.2857%;height:40px;font-size:14px;line-height:40px}.ce-date-day>div:hover{color:#5175f4;opacity:.8}.ce-date-day>div.active{color:#5175f4;font-weight:700}.ce-date-day>div.disable{color:#c0c4cc}.ce-date-day>div.select{color:#fff;background-color:#5175f4}.ce-year-wrap{flex-wrap:wrap;align-items:center;width:100%;min-height:280px;margin-top:15px;display:none}.ce-year-wrap.active{display:flex}.ce-year-wrap>div{text-align:center;color:#606266;cursor:pointer;border-radius:4px;width:33.3333%;height:60px;font-size:14px;line-height:60px}.ce-year-wrap>div:hover{color:#5175f4;opacity:.8}.ce-year-wrap>div.active{color:#5175f4;font-weight:700}.ce-year-wrap>div.select{color:#fff;background-color:#5175f4}.ce-month-wrap{flex-wrap:wrap;align-items:center;width:100%;min-height:280px;margin-top:15px;display:none}.ce-month-wrap.active{display:flex}.ce-month-wrap>div{text-align:center;color:#606266;cursor:pointer;border-radius:4px;width:33.3333%;height:60px;font-size:14px;line-height:60px}.ce-month-wrap>div:hover{color:#5175f4;opacity:.8}.ce-month-wrap>div.active{color:#5175f4;font-weight:700}.ce-month-wrap>div.select{color:#fff;background-color:#5175f4}.ce-time-wrap{height:286px;padding:10px;display:none}.ce-time-wrap ::-webkit-scrollbar{width:0}.ce-time-wrap.active{display:flex}.ce-time-wrap li{list-style:none}.ce-time-wrap>li{text-align:center;width:33.3%;height:100%}.ce-time-wrap>li>span{display:inline-block;transform:translateY(-5px)}.ce-time-wrap>li>ol{border:1px solid #e2e2e2;height:calc(100% - 20px);position:relative;overflow-y:auto}.ce-time-wrap>li:first-child>ol{border-right:0}.ce-time-wrap>li:last-child>ol{border-left:0}.ce-time-wrap>li>ol>li{cursor:pointer;line-height:30px;transition:all .3s}.ce-time-wrap>li>ol>li:hover{background-color:#eaeaea}.ce-time-wrap>li>ol>li.active{color:#fff;background:#5175f4}.ce-date-menu{border-top:1px solid #e4e7ed;justify-content:flex-end;align-items:center;width:100%;height:28px;padding-top:10px;display:flex;position:relative}.ce-date-menu button{white-space:nowrap;cursor:pointer;color:#606266;appearance:none;text-align:center;box-sizing:border-box;-webkit-user-select:none;user-select:none;background:#fff;border:1px solid #dcdfe6;border-radius:3px;outline:none;margin:0 0 0 10px;padding:7px 15px;font-size:12px;font-weight:500;line-height:1;transition:all .1s;display:inline-block}.ce-date-menu button:hover{color:#5175f4;border-color:#5175f4}.ce-date-menu button.ce-date-menu__time{border:1px solid #0000;margin-left:0;position:absolute;left:0}.ce-date-menu button.ce-date-menu__time:hover{color:#5175f4}.ce-block-item{z-index:0;background-color:#fff;border:1px solid #ebecf0;position:absolute}.ce-block-item .ce-resizer-selection{width:100%;height:100%}.ce-block-item .ce-resizer-mask{z-index:1;background-color:#0000;position:absolute;inset:0}.ce-table-tool__row{background-color:#e2e6ed;border-radius:6.5px;width:12px;position:absolute;overflow:hidden}.ce-table-tool__row .ce-table-tool__row__item{cursor:pointer;width:100%;transition:all .3s;position:relative}.ce-table-tool__row .ce-table-tool__row__item:after{content:"";background-color:#c0c6cf;width:8px;height:1px;position:absolute;bottom:0;left:2px}.ce-table-tool__row .ce-table-tool__row__item:hover{background-color:#dadce0}.ce-table-tool__row .ce-table-tool__row__item:last-child:after{display:none}.ce-table-tool__quick__add{cursor:pointer;background-color:#e2e6ed;border-radius:50%;width:16px;height:16px;position:absolute}.ce-table-tool__quick__add:after{content:"+";color:#fff;position:absolute;top:50%;left:50%;transform:translate(-50%,-55%)}.ce-table-tool__select{cursor:pointer;border-radius:3px;width:16px;height:18px;position:absolute}.ce-table-tool__select:hover{background-color:#e2e6ed}.ce-table-tool__select:after{content:":::";color:#aaaaab;position:absolute;top:50%;left:50%;transform:translate(-75%,-50%)rotate(-90deg)}.ce-table-tool__col{background-color:#e2e6ed;border-radius:6.5px;height:12px;display:flex;position:absolute;overflow:hidden}.ce-table-tool__col .ce-table-tool__col__item{cursor:pointer;height:100%;transition:all .3s;position:relative}.ce-table-tool__col .ce-table-tool__col__item:after{content:"";z-index:1;background-color:#c0c6cf;width:1px;height:8px;position:absolute;top:2px;left:-1px}.ce-table-tool__col .ce-table-tool__col__item:hover{background-color:#dadce0}.ce-table-tool__col .ce-table-tool__col__item:first-child:after{display:none}.ce-table-tool__row .ce-table-tool__row__item.active,.ce-table-tool__col .ce-table-tool__col__item.active{background-color:#c4d7fa}.ce-table-tool__col .ce-table-tool__anchor{z-index:9;cursor:col-resize;width:10px;height:12px;position:absolute;right:-5px}.ce-table-tool__row .ce-table-tool__anchor{z-index:9;cursor:row-resize;width:12px;height:10px;position:absolute;bottom:-5px;left:0}.ce-table-anchor__line{z-index:9;border:1px dotted #000;position:absolute}.ce-table-tool__border{z-index:1;pointer-events:none;background:0 0;position:absolute}.ce-table-tool__border__row{cursor:row-resize;pointer-events:auto;position:absolute}.ce-table-tool__border__col{cursor:col-resize;pointer-events:auto;position:absolute}.ce-resizer-selection{pointer-events:none;border:1px solid;position:absolute}.ce-resizer-selection .resizer-handle{z-index:9;box-sizing:border-box;pointer-events:initial;border:2px solid #fff;border-radius:5px;width:10px;height:10px;position:absolute;box-shadow:0 1px 4px #0000004d}.ce-resizer-selection .handle-0{cursor:nw-resize}.ce-resizer-selection .handle-1{cursor:n-resize}.ce-resizer-selection .handle-2{cursor:ne-resize}.ce-resizer-selection .handle-3{cursor:e-resize}.ce-resizer-selection .handle-4{cursor:se-resize}.ce-resizer-selection .handle-5{cursor:s-resize}.ce-resizer-selection .handle-6{cursor:sw-resize}.ce-resizer-selection .handle-7{cursor:w-resize}.ce-resizer-size-view{white-space:nowrap;z-index:9;opacity:.9;background-color:#000;border-radius:4px;align-items:center;height:20px;padding:0 5px;display:flex;position:absolute;top:-30px;left:0}.ce-resizer-size-view span{color:#fff;font-size:12px}.ce-resizer-image{opacity:.5;position:absolute}.ce-image-previewer{z-index:1000;background:#f2f4f7;justify-content:center;align-items:center;width:100%;height:100%;animation:.3s previewerAnimation;display:flex;position:fixed;top:0;left:0;overflow:hidden}@keyframes previewerAnimation{0%{opacity:.1}to{opacity:1}}.ce-image-previewer .image-close{z-index:99;cursor:pointer;background:url("data:image/svg+xml,%3csvg%20width='32'%20height='32'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M23.97%207l1.415%201.414-7.779%207.778%207.779%207.779-1.414%201.414-7.779-7.779-7.778%207.779L7%2023.97l7.778-7.779L7%208.414%208.414%207l7.778%207.778L23.971%207z'%20fill='%233D4757'%20fill-rule='evenodd'/%3e%3c/svg%3e") 0 0/100% 100% no-repeat;border-radius:50%;width:24px;height:24px;transition:all .3s;display:inline-block;position:absolute;top:30px;right:50px}.ce-image-previewer .image-close:hover{background-color:#e2e6ed}.ce-image-previewer .ce-image-container{position:relative}.ce-image-previewer .ce-image-container img{cursor:move;position:relative}.ce-image-previewer .ce-image-menu{z-index:99;justify-content:center;align-items:center;height:50px;display:flex;position:absolute;bottom:50px}.ce-image-previewer .ce-image-menu i{cursor:pointer;background-repeat:no-repeat;background-size:100% 100%;border-radius:50%;width:32px;height:32px;margin:0 8px;transition:all .3s;display:inline-block}.ce-image-previewer .ce-image-menu i:hover{background-color:#e2e6ed}.ce-image-previewer .ce-image-menu i.zoom-in{background-image:url("data:image/svg+xml,%3csvg%20width='32'%20height='32'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M14%2014v-4h2v4h4v2h-4v4h-2v-4h-4v-2h4zm8.749%2010.163A11.952%2011.952%200%200115%2027C8.373%2027%203%2021.627%203%2015S8.373%203%2015%203s12%205.373%2012%2012c0%202.954-1.067%205.658-2.837%207.749l4.908%204.908-1.414%201.414-4.908-4.908zM15%2025c5.523%200%2010-4.477%2010-10S20.523%205%2015%205%205%209.477%205%2015s4.477%2010%2010%2010z'%20fill='%233D4757'/%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu i.zoom-out{background-image:url("data:image/svg+xml,%3csvg%20width='32'%20height='32'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M22.749%2024.163A11.952%2011.952%200%200115%2027C8.373%2027%203%2021.627%203%2015S8.373%203%2015%203s12%205.373%2012%2012c0%202.954-1.067%205.658-2.837%207.749l4.908%204.908-1.414%201.414-4.908-4.908zM15%2025c5.523%200%2010-4.477%2010-10S20.523%205%2015%205%205%209.477%205%2015s4.477%2010%2010%2010zm-5-11h10v2H10v-2z'%20fill='%233D4757'/%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu i.rotate{background-image:url("data:image/svg+xml,%3csvg%20width='32'%20height='32'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M16%204c6.627%200%2012%205.373%2012%2012a11.97%2011.97%200%2001-4%208.944V23h-.86A9.968%209.968%200%200026%2016c0-5.523-4.477-10-10-10S6%2010.477%206%2016c0%205.185%203.947%209.449%209%209.95v2.009C8.84%2027.451%204%2022.291%204%2016%204%209.373%209.373%204%2016%204z'%20fill-rule='nonzero'/%3e%3cpath%20d='M19.879%2027.328l1.767-6.717%204.95%204.95z'/%3e%3c/g%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu i.original-size{background-image:url("data:image/svg+xml,%3csvg%20width='32'%20height='32'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M4%204h24v24H4V4zm2%202v20h20V6H6zm4%205h2v10h-2V11zm5%202h2v2h-2v-2zm0%204h2v2h-2v-2zm5-6h2v10h-2V11z'%20fill='%233D4757'/%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu i.image-download{background-image:url("data:image/svg+xml,%3csvg%20width='24'%20height='24'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M4.5%2015v3.5h15V15H21v5H3v-5h1.5zm8.232-11.226v9.196l4.05-4.05%201.06%201.06-5.834%205.834-5.833-5.833%201.06-1.06%203.998%203.996V3.774h1.5z'%20fill='%233D4757'/%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu .image-navigate{justify-content:center;align-items:center;display:flex}.ce-image-previewer .ce-image-menu i.image-pre{background-image:url("data:image/svg+xml,%3csvg%20width='20'%20height='20'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M12.5%204.063L6.875%2010l5.625%205.938'%20stroke='%233D4757'%20stroke-width='1.5'%20stroke-linecap='round'%20stroke-linejoin='round'/%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu i.image-next{background-image:url("data:image/svg+xml,%3csvg%20width='20'%20height='20'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M7.5%204.063L13.125%2010%207.5%2015.938'%20stroke='%233D4757'%20stroke-width='1.5'%20stroke-linecap='round'%20stroke-linejoin='round'/%3e%3c/svg%3e")}.ce-image-previewer .ce-image-menu .image-count{color:#000;font-size:20px}.ce-image-previewer .ce-image-menu i.disabled{cursor:not-allowed;opacity:.5}.ce-contextmenu-container{z-index:9;background:#fff;border:1px solid #e2e6ed;border-radius:2px;padding:4px;display:none;position:fixed;overflow:hidden auto;box-shadow:0 2px 12px #38383833}.ce-contextmenu-content{flex-direction:column;display:flex}.ce-contextmenu-content .ce-contextmenu-sub-item:after{content:"";background:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20d='M0%200h16v16H0z'/%3e%3cg%20fill='%23767C85'%3e%3cpath%20d='M7%2012.243l-.707-.707%204.243-4.243.707.707z'/%3e%3cpath%20d='M6.293%204.464L7%203.757%2011.243%208l-.707.707z'/%3e%3c/g%3e%3c/g%3e%3c/svg%3e");width:16px;height:16px;position:absolute;right:12px}.ce-contextmenu-content .ce-contextmenu-item{white-space:nowrap;box-sizing:border-box;cursor:pointer;align-items:center;min-width:140px;height:30px;padding:0 32px 0 16px;display:flex}.ce-contextmenu-content .ce-contextmenu-item.hover{background:#1937580a}.ce-contextmenu-content .ce-contextmenu-item span{color:#3d4757;white-space:nowrap;text-overflow:ellipsis;max-width:300px;font-size:12px;overflow:hidden}.ce-contextmenu-content .ce-contextmenu-item span.ce-shortcut{color:#767c85;text-align:right;flex:1;height:30px;margin-left:20px;line-height:30px}.ce-contextmenu-content .ce-contextmenu-item i{vertical-align:middle;background-repeat:no-repeat;background-size:100% 100%;flex-shrink:0;width:16px;height:16px;margin-right:8px;display:inline-block}.ce-contextmenu-divider{background-color:#e2e6ed;height:1px;margin:4px 16px}.ce-contextmenu-print{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20viewBox='0%200%2016%2016'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M12%204h-1V2H5v2H4V2a1%201%200%20011-1h6a1%201%200%20011%201v2zm0%205v4a1%201%200%2001-1%201H5a1%201%200%2001-1-1V9h1v4h6V9h1z'/%3e%3cpath%20d='M12%2012v-1h2V5H2v6h2v1H2a1%201%200%2001-1-1V5a1%201%200%20011-1h12a1%201%200%20011%201v6a1%201%200%2001-1%201h-2z'/%3e%3cpath%20d='M3%208h10v1H3zm8-2h2v1h-2z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-image{background-image:url("data:image/svg+xml,%3csvg%20version='1.1'%20id='图层_1'%20xmlns='http://www.w3.org/2000/svg'%20x='0'%20y='0'%20viewBox='0%200%2016%2016'%20xml:space='preserve'%3e%3cstyle%3e.st0{fill:%233d4757}%3c/style%3e%3cg%20id='_x30_0-公共_x2F_02工具栏_x2F_插入图片-16px-'%3e%3cg%20id='Group-19'%20transform='translate(1%201)'%3e%3cpath%20id='Combined-Shape'%20class='st0'%20d='M1%200h12c.6%200%201%20.4%201%201v11c0%20.6-.4%201-1%201H1c-.6%200-1-.4-1-1V1c0-.6.4-1%201-1zm0%201v11h12V1H1z'/%3e%3ccircle%20id='椭圆形'%20class='st0'%20cx='10'%20cy='4'%20r='1'/%3e%3cpath%20id='Path'%20class='st0'%20d='M8.5%2011.2l-4-4.1L1%2010.7V9.2c1.7-1.6%202.7-2.5%203-2.8.4-.5.7-.4%201%200L8.5%2010%2011%207.3c.4-.5.6-.5%201-.1l2%202.8v1.5l-2.5-3.4-3%203.1z'/%3e%3c/g%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-image-change{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cg%20transform='translate(2%204)'%20fill='%233D4757'%3e%3ccircle%20fill-rule='nonzero'%20cx='3'%20cy='1'%20r='1'/%3e%3cpath%20d='M7.473%208.223L3.47%204.107%200%207.667v-1.5C1.715%204.6%202.707%203.664%202.975%203.358c.402-.457.651-.39%201.042%200L7.473%207%209.96%204.349c.414-.462.62-.462%201.011-.071L13%207.06v1.5l-2.51-3.41-3.017%203.072z'/%3e%3c/g%3e%3cpath%20d='M6%201.5H1.5v12h13v-4V13a.5.5%200%2001-.5.5H2a.5.5%200%2001-.5-.5V2a.5.5%200%2001.5-.5h4zm8.5%208V6l-.5.5h1l-.5-.5v3.5zM6%201.5h4L9.5%201v1l.5-.5H6z'%20stroke='%233D4757'/%3e%3cpath%20d='M13.085%201.316l-3.814%204a1%201%200%20001.458%201.368l3.815-4a1%201%200%2010-1.459-1.368z'%20fill='%233D4757'%20fill-rule='nonzero'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-insert-row-col{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20stroke='%233D4757'%20d='M8.5%205.5h6v4h-6z'/%3e%3cpath%20fill='%233D4757'%20d='M4%207v1h2V7zm-3%20.5L4%205v5zM1%201h12v1H1zm0%2012h12v1H1z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-insert-top-row{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20fill='%233D4757'%20d='M8%205H7v3h1zm-.5-3L10%205H5z'/%3e%3crect%20stroke='%233D4757'%20x='1.5'%20y='10.5'%20width='12'%20height='3'%20rx='1'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-insert-bottom-row{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20fill='%233D4757'%20d='M7%2011h1V8H7zm.5%203L5%2011h5z'/%3e%3crect%20stroke='%233D4757'%20x='1.5'%20y='2.5'%20width='12'%20height='3'%20rx='1'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-insert-left-col{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20fill='%233D4757'%20d='M11%207v1h3V7zm-3%20.5L11%205v5z'/%3e%3crect%20stroke='%233D4757'%20transform='rotate(90%204%207.5)'%20x='-2'%20y='6'%20width='12'%20height='3'%20rx='1'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-insert-right-col{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20fill='%233D4757'%20d='M5%208V7H2v1zm3-.5L5%2010V5z'/%3e%3crect%20stroke='%233D4757'%20transform='rotate(90%2012%207.5)'%20x='6'%20y='6'%20width='12'%20height='3'%20rx='1'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-delete-row-col{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20stroke='%23929AA8'%20d='M8.5%206.5h6v2h-6z'/%3e%3cpath%20fill='%233D4757'%20d='M2%2012h11v1H2zM2%202h11v1H2zm.63%203L7%209.35l-.635.65L2%205.63z'/%3e%3cpath%20fill='%233D4757'%20d='M2%209.363L6.355%205%207%205.707%202.695%2010z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-delete-row{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20stroke='%23929AA8'%20d='M8.5%205.5h6v4h-6z'/%3e%3cpath%20fill='%233D4757'%20d='M1%2013h12v1H1zM1%201h12v1H1zm0%204h1v1H1zm1%201h1v1H2zm1%201h1v1H3zm1-1h1v1H4zm1-1h1v1H5zM4%208h1v1H4zM2%208h1v1H2zm3%201h1v1H5zM1%209h1v1H1z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-delete-col{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='none'%20fill-rule='evenodd'%3e%3cpath%20stroke='%23929AA8'%20d='M5.5%207.5v-6h4v6z'/%3e%3cpath%20fill='%233D4757'%20d='M13%2015V3h1v12zM1%2015V3h1v12zm4%200v-1h1v1zm1-1v-1h1v1zm1-1v-1h1v1zm-1-1v-1h1v1zm-1-1v-1h1v1zm3%201v-1h1v1zm0%202v-1h1v1zm1-3v-1h1v1zm0%204v-1h1v1z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-delete-table{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M14%2013h-1v-3H2v3H1v-3a1%201%200%20011-1h11a1%201%200%20011%201v3z'%20fill-rule='nonzero'/%3e%3cpath%20d='M5.625%202L10%206.375%209.375%207%205%202.625z'/%3e%3cpath%20d='M5%206.375L9.375%202l.625.625L5.625%207z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-merge-cell{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M6%201v1H2v11h4v1H2a1%201%200%2001-1-1V2a1%201%200%20011-1h4zm3%200h4a1%201%200%20011%201v11a1%201%200%2001-1%201H9v-1h4V2H9V1z'/%3e%3cpath%20fill-rule='nonzero'%20d='M6%201h1v4H6zm2%200h1v4H8z'/%3e%3cpath%20d='M8%207.5L10%206v3zm-1%200L5%206v3z'/%3e%3cpath%20d='M9%207h3v1H9zM3%207h3v1H3z'/%3e%3cpath%20fill-rule='nonzero'%20d='M8%2010h1v4H8zm-2%200h1v4H6z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-merge-cancel-cell{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M6%201v1H2v11h4v1H2a1%201%200%2001-1-1V2a1%201%200%20011-1h4zm3%200h4a1%201%200%20011%201v11a1%201%200%2001-1%201H9v-1h4V2H9V1z'/%3e%3cpath%20fill-rule='nonzero'%20d='M6%201h1v4H6zm2%200h1v4H8z'/%3e%3cpath%20d='M3%207.5L5%206v3zm9%200L10%206v3z'/%3e%3cpath%20d='M4%207h3v1H4zm4%200h3v1H8z'/%3e%3cpath%20fill-rule='nonzero'%20d='M8%2010h1v4H8zm-2%200h1v4H6z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-table-auto-fit-content{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M2%202h12a1%201%200%20011%201v10a1%201%200%2001-1%201H2a1%201%200%2001-1-1V3a1%201%200%20011-1zm0%201v10h12V3H2z'/%3e%3cpath%20d='M5%206.5L3%208l2%201.5v-3zm6%200L13%208l-2%201.5v-3z'/%3e%3cpath%20d='M5%207.5h6v1H5z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-table-auto-fit-page{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cg%20fill='%233D4757'%20fill-rule='evenodd'%3e%3cpath%20d='M3%201h10a1%201%200%20011%201v12a1%201%200%2001-1%201H3a1%201%200%2001-1-1V2a1%201%200%20011-1zm0%201v12h10V2H3z'/%3e%3cpath%20d='M6%205.5L4%207l2%201.5v-3zm4%200L12%207l-2%201.5v-3z'/%3e%3cpath%20d='M6%206.5h4v1H6z'/%3e%3cpath%20d='M4%209h8v1H4zm0%202h8v1H4z'/%3e%3c/g%3e%3c/svg%3e")}.ce-contextmenu-vertical-align{background-image:url("data:image/svg+xml,%3csvg%20height='16'%20viewBox='0%200%2016%2016'%20width='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2%2013h12v1H2zm0-3h8v1H2zm0-3h12v1H2zm0-6h12v1H2zm0%203h8v1H2z'%20fill='%233d4757'%20fill-rule='evenodd'/%3e%3c/svg%3e")}.ce-contextmenu-vertical-align-top{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M8%208H7v6h1zm-.5-3L10%208H5zM2%203h11v1H2z'%20fill='%233D4757'%20fill-rule='evenodd'/%3e%3c/svg%3e")}.ce-contextmenu-vertical-align-middle{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20viewBox='0%200%2016%2016'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M8%2012H7v3h1zm-.5-3l2.5%203H5zM7%203h1V0H7zm.5%203L5%203h5zM2%207h11v1H2z'%20fill='%233D4757'%20fill-rule='evenodd'/%3e%3c/svg%3e")}.ce-contextmenu-vertical-align-bottom{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M7%209h1V3H7zm.5%203L5%209h5zM2%2013h11v1H2z'%20fill='%233D4757'%20fill-rule='evenodd'/%3e%3c/svg%3e")}.ce-contextmenu-border-all{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%233D4757'/%3e%3cpath%20fill='%233D4757'%20d='M3%208h11v1H3z'/%3e%3cpath%20fill='%233D4757'%20d='M9%203v11H8V3z'/%3e%3c/svg%3e")}.ce-contextmenu-border-empty{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20fill-rule='evenodd'%20clip-rule='evenodd'%20d='M13%203h-1V2h1a1%201%200%20011%201v1h-1V3zm-3-1v1H8.5v2h-1V3H6V2h4zM4%202v1H3v1H2V3a1%201%200%20011-1h1zM2%206h1v1.5h2v1H3V10H2V6zm0%206h1v1h1v1H3a1%201%200%2001-1-1v-1zm4%202v-1h1.5v-2h1v2H10v1H6zm6%200v-1h1v-1h1v1a1%201%200%2001-1%201h-1zm2-4h-1V8.5h-2v-1h2V6h1v4zM8.5%207.5v-1h-1v1h-1v1h1v1h1v-1h1v-1h-1z'%20fill='%23AAACB0'/%3e%3c/svg%3e")}.ce-contextmenu-border-dash{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20fill-rule='evenodd'%20clip-rule='evenodd'%20d='M13%203h-1V2h1a1%201%200%20011%201v1h-1V3zm-3-1v1H8.5v2h-1V3H6V2h4zM4%202v1H3v1H2V3a1%201%200%20011-1h1zM2%206h1v1.5h2v1H3V10H2V6zm0%206h1v1h1v1H3a1%201%200%2001-1-1v-1zm4%202v-1h1.5v-2h1v2H10v1H6zm6%200v-1h1v-1h1v1a1%201%200%2001-1%201h-1zm2-4h-1V8.5h-2v-1h2V6h1v4zM8.5%207.5v-1h-1v1h-1v1h1v1h1v-1h1v-1h-1z'%20fill='%23000000'/%3e%3c/svg%3e")}.ce-contextmenu-border-external{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%233D4757'/%3e%3cpath%20fill-rule='evenodd'%20clip-rule='evenodd'%20d='M9%205V3H8v2h1zm0%209v-2H8v2h1zM5%208H3v1h2V8zm9%200h-2v1h2V8zM9%207v1h1v1H9v1H8V9H7V8h1V7h1z'%20fill='%23AAACB0'/%3e%3c/svg%3e")}.ce-contextmenu-border-internal{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'/%3e%3cpath%20fill-rule='evenodd'%20clip-rule='evenodd'%20d='M9%205V3H8v2h1zm0%209v-2H8v2h1zM5%208H3v1h2V8zm9%200h-2v1h2V8zM9%207v1h1v1H9v1H8V9H7V8h1V7h1z'%20fill='%233D4757'/%3e%3c/svg%3e")}.ce-contextmenu-border-td{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'/%3e%3cpath%20stroke='%233D4757'%20d='M8.5%202.5%20v6%20h-6'/%3e%3c/svg%3e")}.ce-contextmenu-border-td-top{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'/%3e%3cpath%20stroke='%233D4757'%20stroke-width='2'%20d='M2.5%203%20h12'/%3e%3c/svg%3e")}.ce-contextmenu-border-td-left{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'/%3e%3cpath%20stroke='%233D4757'%20stroke-width='2'%20d='M3%203%20v11'/%3e%3c/svg%3e")}.ce-contextmenu-border-td-bottom{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'/%3e%3cpath%20stroke='%233D4757'%20stroke-width='2'%20d='M2.5%2014%20h12'/%3e%3c/svg%3e")}.ce-contextmenu-border-td-right{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'/%3e%3cpath%20stroke='%233D4757'%20stroke-width='2'%20d='M14%203%20v11'/%3e%3c/svg%3e")}.ce-contextmenu-border-td-forward{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'%20/%3e%3cpath%20stroke='%233D4757'%20d='M14%203%20l-11%2011'%20/%3e%3c/svg%3e")}.ce-contextmenu-border-td-back{background-image:url("data:image/svg+xml,%3csvg%20width='16'%20height='16'%20fill='none'%20xmlns='http://www.w3.org/2000/svg'%3e%3cpath%20d='M2.5%203a.5.5%200%2001.5-.5h11a.5.5%200%2001.5.5v11a.5.5%200%2001-.5.5H3a.5.5%200%2001-.5-.5V3z'%20stroke='%23AAACB0'%20/%3e%3cpath%20stroke='%233D4757'%20d='M3%203%20l11%2011'%20/%3e%3c/svg%3e")}.ce-hyperlink-popup{color:#3d4757;z-index:1;text-align:center;background:#fff;border-radius:2px;padding:12px 16px;display:none;position:absolute;box-shadow:0 2px 12px #626b8433}.ce-hyperlink-popup a{white-space:nowrap;text-overflow:ellipsis;cursor:pointer;color:#00f;border-bottom-style:solid;border-bottom-width:1px;min-width:100px;max-width:300px;font-size:12px;text-decoration:none;display:inline-block;overflow:hidden}.ce-zone-indicator>div{color:#000;transform-origin:0 0;background:#dae7fc;padding:3px 6px;font-size:12px;position:absolute}.ce-zone-indicator-border__top,.ce-zone-indicator-border__bottom,.ce-zone-indicator-border__left,.ce-zone-indicator-border__right{z-index:0;display:block;position:absolute}.ce-zone-indicator-border__top{border-top:2px dashed #eee}.ce-zone-indicator-border__bottom{border-top:2px dashed #eee;width:100%}.ce-zone-indicator-border__left{border-left:2px dashed #eee}.ce-zone-indicator-border__right{border-right:2px dashed #eee}.ce-zone-tip{white-space:nowrap;opacity:.9;z-index:9;-webkit-user-select:none;user-select:none;pointer-events:none;background-color:#000;border-radius:4px;outline:none;align-items:center;height:30px;padding:0 5px;transition:all .3s;display:none;position:fixed;transform:translate(10px,10px)}.ce-zone-tip.show{display:flex}.ce-zone-tip span{color:#fff;font-size:12px}.ce-magnifier{pointer-events:none;z-index:9999;border-radius:50%;display:none;position:fixed;box-shadow:0 4px 12px #00000040}.ce-sr-only{z-index:-1;clip:rect(0, 0, 0, 0);clip-path:inset(50%);white-space:nowrap;pointer-events:none;border:0;width:1px;height:1px;margin:-1px;padding:0;position:absolute;top:0;left:0;overflow:hidden}.ce-trace-popup{color:#3d4757;z-index:1;pointer-events:none;background:#fff;border-radius:4px;padding:8px 12px;font-size:12px;line-height:1.6;display:none;position:absolute;box-shadow:0 2px 12px #626b8433}.ce-trace-popup__list{flex-direction:column;gap:6px;display:flex}.ce-trace-popup__item{white-space:nowrap;align-items:center;gap:8px;display:flex}.ce-trace-popup__type{font-size:13px;font-weight:600}.ce-trace-popup__author,.ce-trace-popup__time{color:#6b7280}.ce-hint-popup{color:#000;z-index:1;word-break:break-word;pointer-events:none;background:#fff;border-radius:4px;max-width:280px;padding:6px 10px;font-size:12px;line-height:1.6;display:none;position:absolute;box-shadow:0 2px 12px #626b8433}.ce-hint-popup__text{white-space:pre-wrap}.ce-ruler{z-index:2;-webkit-user-select:none;user-select:none;pointer-events:none;width:100%;height:100%;position:absolute;top:0;left:0}.ce-ruler-x{pointer-events:auto;display:block;position:sticky;top:0;box-shadow:0 1px 3px #0000001a}.ce-ruler-y{pointer-events:auto;position:absolute;top:0;left:0;box-shadow:1px 0 3px #0000001a}.ce-inputarea{letter-spacing:0;z-index:-1;resize:none;color:#0000;-webkit-user-select:none;user-select:none;caret-color:#0000;background-color:#0000;border:none;outline:none;width:100px;min-width:0;height:30px;min-height:0;margin:0;padding:0;font-size:12px;position:absolute;top:0;left:0;overflow:hidden}.ce-cursor{pointer-events:none;background-color:#000;outline:none;width:1px;height:20px;position:absolute;left:0;right:0}.ce-cursor.ce-cursor--animation{animation-name:cursorAnimation;animation-duration:1s;animation-iteration-count:infinite}@keyframes cursorAnimation{0%{opacity:1}13%{opacity:0}50%{opacity:0}63%{opacity:1}to{opacity:1}}.ce-float-image{opacity:.5;pointer-events:none;position:absolute}/*$vite$:1*/`)),document.head.appendChild(e)}}catch(e){console.error(`vite-plugin-css-injected-by-js`,e)}})();
//#region package.json
var e = "1.0.2", t;
(function(e) {
	e.HALF = "half", e.ONE_THIRD = "one-third", e.QUARTER = "quarter";
})(t ||= {});
var n;
(function(e) {
	e.ARABIC = "arabic", e.CHINESE = "chinese";
})(n ||= {});
var r;
(function(e) {
	e.INLINE = "inline", e.BLOCK = "block", e.SURROUND = "surround", e.FLOAT_TOP = "float-top", e.FLOAT_BOTTOM = "float-bottom";
})(r ||= {});
var i;
(function(e) {
	e.BEFORE = "before", e.AFTER = "after", e.OUTER_BEFORE = "outer-before", e.OUTER_AFTER = "outer-after";
})(i ||= {});
var a;
(function(e) {
	e.ROW = "row", e.COLUMN = "column";
})(a ||= {});
//#endregion
//#region src/editor/dataset/constant/Common.ts
var o = "&nbsp;", s = [
	"·",
	"、",
	":",
	"：",
	",",
	"，",
	".",
	"。",
	";",
	"；",
	"?",
	"？",
	"!",
	"！"
], c = {
	[t.HALF]: 1 / 2,
	[t.ONE_THIRD]: 1 / 3,
	[t.QUARTER]: 1 / 4
}, l = {
	ENGLISH: "A-Za-z",
	SPANISH: "A-Za-zÁÉÍÓÚáéíóúÑñÜü",
	FRENCH: "A-Za-zÀÂÇàâçÉéÈèÊêËëÎîÏïÔôÙùÛûŸÿ",
	GERMAN: "A-Za-zÄäÖöÜüß",
	RUSSIAN: "А-Яа-яЁё",
	PORTUGUESE: "A-Za-zÁÉÍÓÚáéíóúÃÕãõÇç",
	ITALIAN: "A-Za-zÀàÈèÉéÌìÍíÎîÓóÒòÙù",
	DUTCH: "A-Za-zÀàÁáÂâÄäÈèÉéÊêËëÌìÍíÎîÏïÓóÒòÔôÖöÙùÛûÜü",
	SWEDISH: "A-Za-zÅåÄäÖö",
	GREEK: "ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω"
}, u;
(function(e) {
	e.LEFT = "left", e.CENTER = "center", e.RIGHT = "right", e.ALIGNMENT = "alignment", e.JUSTIFY = "justify";
})(u ||= {});
//#endregion
//#region src/editor/dataset/enum/Editor.ts
var d;
(function(e) {
	e.COMPONENT = "component", e.MENU = "menu", e.MAIN = "main", e.FOOTER = "footer", e.CONTEXTMENU = "contextmenu", e.POPUP = "popup", e.CATALOG = "catalog", e.COMMENT = "comment";
})(d ||= {});
var f;
(function(e) {
	e.PAGE = "page", e.TABLE = "table";
})(f ||= {});
var p;
(function(e) {
	e.EDIT = "edit", e.CLEAN = "clean", e.READONLY = "readonly", e.FORM = "form", e.PRINT = "print", e.DESIGN = "design", e.GRAFFITI = "graffiti", e.TRACE = "trace";
})(p ||= {});
var m;
(function(e) {
	e.HEADER = "header", e.MAIN = "main", e.FOOTER = "footer";
})(m ||= {});
var h;
(function(e) {
	e.PAGING = "paging", e.CONTINUITY = "continuity";
})(h ||= {});
var g;
(function(e) {
	e.VERTICAL = "vertical", e.HORIZONTAL = "horizontal";
})(g ||= {});
var _;
(function(e) {
	e.BREAK_ALL = "break-all", e.BREAK_WORD = "break-word";
})(_ ||= {});
var v;
(function(e) {
	e.SPEED = "speed", e.COMPATIBILITY = "compatibility";
})(v ||= {});
//#endregion
//#region src/editor/core/draw/column/ColumnManager.ts
var y = class {
	draw;
	options;
	layoutMap;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.layoutMap = /* @__PURE__ */ new Map();
	}
	computeLayout(e, t) {
		if (!t) return null;
		let n = Math.max(1, Math.floor(t.count));
		if (n === 1) return null;
		let r = (t.gap ?? this.options.column.gap) * this.options.scale, i = e / n * .5, a = Math.max(0, Math.min(r, i)), o = (e - a * (n - 1)) / n, s = [];
		for (let e = 0; e < n; e++) s.push(e * (o + a));
		return {
			count: n,
			width: o,
			gap: a,
			separator: t.separator ?? !1,
			offsets: s
		};
	}
	compute() {
		this.layoutMap.set(g.VERTICAL, this.computeLayout(this.draw.getInnerWidth(g.VERTICAL), this.options.column)), this.layoutMap.set(g.HORIZONTAL, this.computeLayout(this.draw.getInnerWidth(g.HORIZONTAL), this.options.column));
	}
	getLayout(e = this.options.paperDirection) {
		return this.layoutMap.get(e) || null;
	}
	setConfig(e) {
		!e || e.count <= 1 ? this.options.column = {
			...this.options.column,
			count: 1
		} : this.options.column = {
			...this.options.column,
			...e,
			count: Math.max(1, Math.floor(e.count))
		};
	}
	getOffset(e, t) {
		let n = this.getLayout(t);
		return !n || e === void 0 || e < 0 || e >= n.count ? 0 : n.offsets[e];
	}
	drawSeparator(e, t) {
		let n = this.draw.getPageDirection(t), r = this.getLayout(n);
		if (!r || !r.separator || r.count < 2) return;
		let { column: i, scale: a } = this.options, { margins: o, height: s } = this.draw.getPageSize(t), c = o[3], l = o[0] + this.draw.getHeader().getExtraHeight(t), u = s - o[2] - this.draw.getFooter().getExtraHeight(t);
		e.save(), e.strokeStyle = i.separatorColor, e.lineWidth = i.separatorWidth * a, e.beginPath();
		for (let t = 1; t < r.count; t++) {
			let n = c + r.offsets[t] - r.gap / 2;
			e.moveTo(n + .5, l), e.lineTo(n + .5, u);
		}
		e.stroke(), e.restore();
	}
}, b = /[0-9.]/, x = RegExp("[#*0-9]\\uFE0F?\\u20E3|[\\xA9\\xAE\\u203C\\u2049\\u2122\\u2139\\u2194-\\u2199\\u21A9\\u21AA\\u231A\\u231B\\u2328\\u23CF\\u23ED-\\u23EF\\u23F1\\u23F2\\u23F8-\\u23FA\\u24C2\\u25AA\\u25AB\\u25B6\\u25C0\\u25FB\\u25FC\\u25FE\\u2600-\\u2604\\u260E\\u2611\\u2614\\u2615\\u2618\\u2620\\u2622\\u2623\\u2626\\u262A\\u262E\\u262F\\u2638-\\u263A\\u2640\\u2642\\u2648-\\u2653\\u265F\\u2660\\u2663\\u2665\\u2666\\u2668\\u267B\\u267E\\u267F\\u2692\\u2694-\\u2697\\u2699\\u269B\\u269C\\u26A0\\u26A7\\u26AA\\u26B0\\u26B1\\u26BD\\u26BE\\u26C4\\u26C8\\u26CF\\u26D1\\u26E9\\u26F0-\\u26F5\\u26F7\\u26F8\\u26FA\\u2702\\u2708\\u2709\\u270F\\u2712\\u2714\\u2716\\u271D\\u2721\\u2733\\u2734\\u2744\\u2747\\u2757\\u2763\\u27A1\\u2934\\u2935\\u2B05-\\u2B07\\u2B1B\\u2B1C\\u2B55\\u3030\\u303D\\u3297\\u3299]\\uFE0F?|[\\u261D\\u270C\\u270D](?:\\uFE0F|\\uD83C[\\uDFFB-\\uDFFF])?|[\\u270A\\u270B](?:\\uD83C[\\uDFFB-\\uDFFF])?|[\\u23E9-\\u23EC\\u23F0\\u23F3\\u25FD\\u2693\\u26A1\\u26AB\\u26C5\\u26CE\\u26D4\\u26EA\\u26FD\\u2705\\u2728\\u274C\\u274E\\u2753-\\u2755\\u2795-\\u2797\\u27B0\\u27BF\\u2B50]|\\u26D3\\uFE0F?(?:\\u200D\\uD83D\\uDCA5)?|\\u26F9(?:\\uFE0F|\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|\\u2764\\uFE0F?(?:\\u200D(?:\\uD83D\\uDD25|\\uD83E\\uDE79))?|\\uD83C(?:[\\uDC04\\uDD70\\uDD71\\uDD7E\\uDD7F\\uDE02\\uDE37\\uDF21\\uDF24-\\uDF2C\\uDF36\\uDF7D\\uDF96\\uDF97\\uDF99-\\uDF9B\\uDF9E\\uDF9F\\uDFCD\\uDFCE\\uDFD4-\\uDFDF\\uDFF5\\uDFF7]\\uFE0F?|[\\uDF85\\uDFC2\\uDFC7](?:\\uD83C[\\uDFFB-\\uDFFF])?|[\\uDFC4\\uDFCA](?:\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|[\\uDFCB\\uDFCC](?:\\uFE0F|\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|[\\uDCCF\\uDD8E\\uDD91-\\uDD9A\\uDE01\\uDE1A\\uDE2F\\uDE32-\\uDE36\\uDE38-\\uDE3A\\uDE50\\uDE51\\uDF00-\\uDF20\\uDF2D-\\uDF35\\uDF37-\\uDF43\\uDF45-\\uDF4A\\uDF4C-\\uDF7C\\uDF7E-\\uDF84\\uDF86-\\uDF93\\uDFA0-\\uDFC1\\uDFC5\\uDFC6\\uDFC8\\uDFC9\\uDFCF-\\uDFD3\\uDFE0-\\uDFF0\\uDFF8-\\uDFFF]|\\uDDE6\\uD83C[\\uDDE8-\\uDDEC\\uDDEE\\uDDF1\\uDDF2\\uDDF4\\uDDF6-\\uDDFA\\uDDFC\\uDDFD\\uDDFF]|\\uDDE7\\uD83C[\\uDDE6\\uDDE7\\uDDE9-\\uDDEF\\uDDF1-\\uDDF4\\uDDF6-\\uDDF9\\uDDFB\\uDDFC\\uDDFE\\uDDFF]|\\uDDE8\\uD83C[\\uDDE6\\uDDE8\\uDDE9\\uDDEB-\\uDDEE\\uDDF0-\\uDDF5\\uDDF7\\uDDFA-\\uDDFF]|\\uDDE9\\uD83C[\\uDDEA\\uDDEC\\uDDEF\\uDDF0\\uDDF2\\uDDF4\\uDDFF]|\\uDDEA\\uD83C[\\uDDE6\\uDDE8\\uDDEA\\uDDEC\\uDDED\\uDDF7-\\uDDFA]|\\uDDEB\\uD83C[\\uDDEE-\\uDDF0\\uDDF2\\uDDF4\\uDDF7]|\\uDDEC\\uD83C[\\uDDE6\\uDDE7\\uDDE9-\\uDDEE\\uDDF1-\\uDDF3\\uDDF5-\\uDDFA\\uDDFC\\uDDFE]|\\uDDED\\uD83C[\\uDDF0\\uDDF2\\uDDF3\\uDDF7\\uDDF9\\uDDFA]|\\uDDEE\\uD83C[\\uDDE8-\\uDDEA\\uDDF1-\\uDDF4\\uDDF6-\\uDDF9]|\\uDDEF\\uD83C[\\uDDEA\\uDDF2\\uDDF4\\uDDF5]|\\uDDF0\\uD83C[\\uDDEA\\uDDEC-\\uDDEE\\uDDF2\\uDDF3\\uDDF5\\uDDF7\\uDDFC\\uDDFE\\uDDFF]|\\uDDF1\\uD83C[\\uDDE6-\\uDDE8\\uDDEE\\uDDF0\\uDDF7-\\uDDFB\\uDDFE]|\\uDDF2\\uD83C[\\uDDE6\\uDDE8-\\uDDED\\uDDF0-\\uDDFF]|\\uDDF3\\uD83C[\\uDDE6\\uDDE8\\uDDEA-\\uDDEC\\uDDEE\\uDDF1\\uDDF4\\uDDF5\\uDDF7\\uDDFA\\uDDFF]|\\uDDF4\\uD83C\\uDDF2|\\uDDF5\\uD83C[\\uDDE6\\uDDEA-\\uDDED\\uDDF0-\\uDDF3\\uDDF7-\\uDDF9\\uDDFC\\uDDFE]|\\uDDF6\\uD83C\\uDDE6|\\uDDF7\\uD83C[\\uDDEA\\uDDF4\\uDDF8\\uDDFA\\uDDFC]|\\uDDF8\\uD83C[\\uDDE6-\\uDDEA\\uDDEC-\\uDDF4\\uDDF7-\\uDDF9\\uDDFB\\uDDFD-\\uDDFF]|\\uDDF9\\uD83C[\\uDDE6\\uDDE8\\uDDE9\\uDDEB-\\uDDED\\uDDEF-\\uDDF4\\uDDF7\\uDDF9\\uDDFB\\uDDFC\\uDDFF]|\\uDDFA\\uD83C[\\uDDE6\\uDDEC\\uDDF2\\uDDF3\\uDDF8\\uDDFE\\uDDFF]|\\uDDFB\\uD83C[\\uDDE6\\uDDE8\\uDDEA\\uDDEC\\uDDEE\\uDDF3\\uDDFA]|\\uDDFC\\uD83C[\\uDDEB\\uDDF8]|\\uDDFD\\uD83C\\uDDF0|\\uDDFE\\uD83C[\\uDDEA\\uDDF9]|\\uDDFF\\uD83C[\\uDDE6\\uDDF2\\uDDFC]|\\uDF44(?:\\u200D\\uD83D\\uDFEB)?|\\uDF4B(?:\\u200D\\uD83D\\uDFE9)?|\\uDFC3(?:\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D(?:[\\u2640\\u2642]\\uFE0F?(?:\\u200D\\u27A1\\uFE0F?)?|\\u27A1\\uFE0F?))?|\\uDFF3\\uFE0F?(?:\\u200D(?:\\u26A7\\uFE0F?|\\uD83C\\uDF08))?|\\uDFF4(?:\\u200D\\u2620\\uFE0F?|\\uDB40\\uDC67\\uDB40\\uDC62\\uDB40(?:\\uDC65\\uDB40\\uDC6E\\uDB40\\uDC67|\\uDC73\\uDB40\\uDC63\\uDB40\\uDC74|\\uDC77\\uDB40\\uDC6C\\uDB40\\uDC73)\\uDB40\\uDC7F)?)|\\uD83D(?:[\\uDC3F\\uDCFD\\uDD49\\uDD4A\\uDD6F\\uDD70\\uDD73\\uDD76-\\uDD79\\uDD87\\uDD8A-\\uDD8D\\uDDA5\\uDDA8\\uDDB1\\uDDB2\\uDDBC\\uDDC2-\\uDDC4\\uDDD1-\\uDDD3\\uDDDC-\\uDDDE\\uDDE1\\uDDE3\\uDDE8\\uDDEF\\uDDF3\\uDDFA\\uDECB\\uDECD-\\uDECF\\uDEE0-\\uDEE5\\uDEE9\\uDEF0\\uDEF3]\\uFE0F?|[\\uDC42\\uDC43\\uDC46-\\uDC50\\uDC66\\uDC67\\uDC6B-\\uDC6D\\uDC72\\uDC74-\\uDC76\\uDC78\\uDC7C\\uDC83\\uDC85\\uDC8F\\uDC91\\uDCAA\\uDD7A\\uDD95\\uDD96\\uDE4C\\uDE4F\\uDEC0\\uDECC](?:\\uD83C[\\uDFFB-\\uDFFF])?|[\\uDC6E\\uDC70\\uDC71\\uDC73\\uDC77\\uDC81\\uDC82\\uDC86\\uDC87\\uDE45-\\uDE47\\uDE4B\\uDE4D\\uDE4E\\uDEA3\\uDEB4\\uDEB5](?:\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|[\\uDD74\\uDD90](?:\\uFE0F|\\uD83C[\\uDFFB-\\uDFFF])?|[\\uDC00-\\uDC07\\uDC09-\\uDC14\\uDC16-\\uDC25\\uDC27-\\uDC3A\\uDC3C-\\uDC3E\\uDC40\\uDC44\\uDC45\\uDC51-\\uDC65\\uDC6A\\uDC79-\\uDC7B\\uDC7D-\\uDC80\\uDC84\\uDC88-\\uDC8E\\uDC90\\uDC92-\\uDCA9\\uDCAB-\\uDCFC\\uDCFF-\\uDD3D\\uDD4B-\\uDD4E\\uDD50-\\uDD67\\uDDA4\\uDDFB-\\uDE2D\\uDE2F-\\uDE34\\uDE37-\\uDE41\\uDE43\\uDE44\\uDE48-\\uDE4A\\uDE80-\\uDEA2\\uDEA4-\\uDEB3\\uDEB7-\\uDEBF\\uDEC1-\\uDEC5\\uDED0-\\uDED2\\uDED5-\\uDED7\\uDEDC-\\uDEDF\\uDEEB\\uDEEC\\uDEF4-\\uDEFC\\uDFE0-\\uDFEB\\uDFF0]|\\uDC08(?:\\u200D\\u2B1B)?|\\uDC15(?:\\u200D\\uD83E\\uDDBA)?|\\uDC26(?:\\u200D(?:\\u2B1B|\\uD83D\\uDD25))?|\\uDC3B(?:\\u200D\\u2744\\uFE0F?)?|\\uDC41\\uFE0F?(?:\\u200D\\uD83D\\uDDE8\\uFE0F?)?|\\uDC68(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?\\uDC68|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D(?:[\\uDC68\\uDC69]\\u200D\\uD83D(?:\\uDC66(?:\\u200D\\uD83D\\uDC66)?|\\uDC67(?:\\u200D\\uD83D[\\uDC66\\uDC67])?)|[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uDC66(?:\\u200D\\uD83D\\uDC66)?|\\uDC67(?:\\u200D\\uD83D[\\uDC66\\uDC67])?)|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]))|\\uD83C(?:\\uDFFB(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?\\uDC68\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D\\uDC68\\uD83C[\\uDFFC-\\uDFFF])))?|\\uDFFC(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?\\uDC68\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D\\uDC68\\uD83C[\\uDFFB\\uDFFD-\\uDFFF])))?|\\uDFFD(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?\\uDC68\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D\\uDC68\\uD83C[\\uDFFB\\uDFFC\\uDFFE\\uDFFF])))?|\\uDFFE(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?\\uDC68\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D\\uDC68\\uD83C[\\uDFFB-\\uDFFD\\uDFFF])))?|\\uDFFF(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?\\uDC68\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D\\uDC68\\uD83C[\\uDFFB-\\uDFFE])))?))?|\\uDC69(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:\\uDC8B\\u200D\\uD83D)?[\\uDC68\\uDC69]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D(?:[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uDC66(?:\\u200D\\uD83D\\uDC66)?|\\uDC67(?:\\u200D\\uD83D[\\uDC66\\uDC67])?|\\uDC69\\u200D\\uD83D(?:\\uDC66(?:\\u200D\\uD83D\\uDC66)?|\\uDC67(?:\\u200D\\uD83D[\\uDC66\\uDC67])?))|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]))|\\uD83C(?:\\uDFFB(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:[\\uDC68\\uDC69]|\\uDC8B\\u200D\\uD83D[\\uDC68\\uDC69])\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D[\\uDC68\\uDC69]\\uD83C[\\uDFFC-\\uDFFF])))?|\\uDFFC(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:[\\uDC68\\uDC69]|\\uDC8B\\u200D\\uD83D[\\uDC68\\uDC69])\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D[\\uDC68\\uDC69]\\uD83C[\\uDFFB\\uDFFD-\\uDFFF])))?|\\uDFFD(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:[\\uDC68\\uDC69]|\\uDC8B\\u200D\\uD83D[\\uDC68\\uDC69])\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D[\\uDC68\\uDC69]\\uD83C[\\uDFFB\\uDFFC\\uDFFE\\uDFFF])))?|\\uDFFE(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:[\\uDC68\\uDC69]|\\uDC8B\\u200D\\uD83D[\\uDC68\\uDC69])\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D[\\uDC68\\uDC69]\\uD83C[\\uDFFB-\\uDFFD\\uDFFF])))?|\\uDFFF(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D\\uD83D(?:[\\uDC68\\uDC69]|\\uDC8B\\u200D\\uD83D[\\uDC68\\uDC69])\\uD83C[\\uDFFB-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83D[\\uDC68\\uDC69]\\uD83C[\\uDFFB-\\uDFFE])))?))?|\\uDC6F(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|\\uDD75(?:\\uFE0F|\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|\\uDE2E(?:\\u200D\\uD83D\\uDCA8)?|\\uDE35(?:\\u200D\\uD83D\\uDCAB)?|\\uDE36(?:\\u200D\\uD83C\\uDF2B\\uFE0F?)?|\\uDE42(?:\\u200D[\\u2194\\u2195]\\uFE0F?)?|\\uDEB6(?:\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D(?:[\\u2640\\u2642]\\uFE0F?(?:\\u200D\\u27A1\\uFE0F?)?|\\u27A1\\uFE0F?))?)|\\uD83E(?:[\\uDD0C\\uDD0F\\uDD18-\\uDD1F\\uDD30-\\uDD34\\uDD36\\uDD77\\uDDB5\\uDDB6\\uDDBB\\uDDD2\\uDDD3\\uDDD5\\uDEC3-\\uDEC5\\uDEF0\\uDEF2-\\uDEF8](?:\\uD83C[\\uDFFB-\\uDFFF])?|[\\uDD26\\uDD35\\uDD37-\\uDD39\\uDD3D\\uDD3E\\uDDB8\\uDDB9\\uDDCD\\uDDCF\\uDDD4\\uDDD6-\\uDDDD](?:\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|[\\uDDDE\\uDDDF](?:\\u200D[\\u2640\\u2642]\\uFE0F?)?|[\\uDD0D\\uDD0E\\uDD10-\\uDD17\\uDD20-\\uDD25\\uDD27-\\uDD2F\\uDD3A\\uDD3F-\\uDD45\\uDD47-\\uDD76\\uDD78-\\uDDB4\\uDDB7\\uDDBA\\uDDBC-\\uDDCC\\uDDD0\\uDDE0-\\uDDFF\\uDE70-\\uDE7C\\uDE80-\\uDE88\\uDE90-\\uDEBD\\uDEBF-\\uDEC2\\uDECE-\\uDEDB\\uDEE0-\\uDEE8]|\\uDD3C(?:\\u200D[\\u2640\\u2642]\\uFE0F?|\\uD83C[\\uDFFB-\\uDFFF])?|\\uDDCE(?:\\uD83C[\\uDFFB-\\uDFFF])?(?:\\u200D(?:[\\u2640\\u2642]\\uFE0F?(?:\\u200D\\u27A1\\uFE0F?)?|\\u27A1\\uFE0F?))?|\\uDDD1(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF84\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83E\\uDDD1|\\uDDD1\\u200D\\uD83E\\uDDD2(?:\\u200D\\uD83E\\uDDD2)?|\\uDDD2(?:\\u200D\\uD83E\\uDDD2)?))|\\uD83C(?:\\uDFFB(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D(?:\\uD83D\\uDC8B\\u200D)?\\uD83E\\uDDD1\\uD83C[\\uDFFC-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF84\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFF])))?|\\uDFFC(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D(?:\\uD83D\\uDC8B\\u200D)?\\uD83E\\uDDD1\\uD83C[\\uDFFB\\uDFFD-\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF84\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFF])))?|\\uDFFD(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D(?:\\uD83D\\uDC8B\\u200D)?\\uD83E\\uDDD1\\uD83C[\\uDFFB\\uDFFC\\uDFFE\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF84\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFF])))?|\\uDFFE(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D(?:\\uD83D\\uDC8B\\u200D)?\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFD\\uDFFF]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF84\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFF])))?|\\uDFFF(?:\\u200D(?:[\\u2695\\u2696\\u2708]\\uFE0F?|\\u2764\\uFE0F?\\u200D(?:\\uD83D\\uDC8B\\u200D)?\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFE]|\\uD83C[\\uDF3E\\uDF73\\uDF7C\\uDF84\\uDF93\\uDFA4\\uDFA8\\uDFEB\\uDFED]|\\uD83D[\\uDCBB\\uDCBC\\uDD27\\uDD2C\\uDE80\\uDE92]|\\uD83E(?:[\\uDDAF\\uDDBC\\uDDBD](?:\\u200D\\u27A1\\uFE0F?)?|[\\uDDB0-\\uDDB3]|\\uDD1D\\u200D\\uD83E\\uDDD1\\uD83C[\\uDFFB-\\uDFFF])))?))?|\\uDEF1(?:\\uD83C(?:\\uDFFB(?:\\u200D\\uD83E\\uDEF2\\uD83C[\\uDFFC-\\uDFFF])?|\\uDFFC(?:\\u200D\\uD83E\\uDEF2\\uD83C[\\uDFFB\\uDFFD-\\uDFFF])?|\\uDFFD(?:\\u200D\\uD83E\\uDEF2\\uD83C[\\uDFFB\\uDFFC\\uDFFE\\uDFFF])?|\\uDFFE(?:\\u200D\\uD83E\\uDEF2\\uD83C[\\uDFFB-\\uDFFD\\uDFFF])?|\\uDFFF(?:\\u200D\\uD83E\\uDEF2\\uD83C[\\uDFFB-\\uDFFE])?))?)|[\\uD800-\\uDBFF][\\uDC00-\\uDFFF]", "g"), S = /[、，。？！；：……「」“”‘’*（）【】〔〕〖〗〘〙〚〛《》———﹝﹞–—\\/·.,!?;:`~<>()[\]{}'"|]/, C = /* @__PURE__ */ RegExp("^[​\n]"), w = /[^0-9\+\-\.eE,]/, T = /\s/;
//#endregion
//#region src/editor/utils/index.ts
function E(e, t) {
	let n;
	return function(...r) {
		n && window.clearTimeout(n), n = window.setTimeout(() => {
			e.apply(this, r);
		}, t);
	};
}
function D(e, t) {
	let n = 0, r;
	return function(...i) {
		let a = Date.now();
		a - n >= t ? (window.clearTimeout(r), e.apply(this, i), n = a) : (window.clearTimeout(r), r = window.setTimeout(() => {
			e.apply(this, i), n = a;
		}, t));
	};
}
function O(e, t) {
	if (!e || typeof e != "object") return e;
	let n = {};
	return Array.isArray(e) ? n = e.map((e) => O(e, t)) : Object.keys(e).forEach((r) => {
		t.includes(r) || (n[r] = O(e[r], t));
	}), n;
}
function k(e) {
	if (typeof structuredClone == "function") return structuredClone(e);
	if (!e || typeof e != "object") return e;
	let t = {};
	return Array.isArray(e) ? t = e.map((e) => k(e)) : Object.keys(e).forEach((n) => {
		t[n] = k(e[n]);
	}), t;
}
function A(e) {
	return e && e.nodeType === 1 && e.tagName.toLowerCase() === "body";
}
function j(e, t, n) {
	if (e && !A(e)) for (e = n ? e : e.parentNode; e;) {
		if (!t || t(e) || A(e)) return t && !t(e) && A(e) ? null : e;
		e = e.parentNode;
	}
	return null;
}
function M() {
	function e() {
		return ((1 + Math.random()) * 65536 | 0).toString(16).substring(1);
	}
	return e() + e() + "-" + e() + "-" + e() + "-" + e() + "-" + e() + e() + e();
}
function N(e) {
	let t = [];
	if (Intl.Segmenter) {
		let n = new Intl.Segmenter().segment(e);
		for (let { segment: e } of n) t.push(e);
	} else {
		let n = /* @__PURE__ */ new Map();
		for (let t of e.matchAll(x)) n.set(t.index, t[0]);
		let r = 0;
		for (; r < e.length;) {
			let i = n.get(r);
			i ? (t.push(i), r += i.length) : (t.push(e[r]), r++);
		}
	}
	return t;
}
function ee(e, t) {
	let n = document.createElement("a");
	n.href = e, n.download = t, n.click();
}
function P(e, t) {
	F(3, e, t);
}
function F(e, t, n) {
	let r = 0, i = 0;
	t.addEventListener("click", function(t) {
		r = (/* @__PURE__ */ new Date()).getTime() - i < 300 ? r + 1 : 0, i = (/* @__PURE__ */ new Date()).getTime(), r >= e - 1 && (n(t), r = 0);
	});
}
function I(e) {
	return Object.prototype.toString.call(e) === "[object Object]";
}
function te(e) {
	return Array.isArray(e);
}
function L(e) {
	return Object.prototype.toString.call(e) === "[object Number]";
}
function ne(e) {
	return Object.prototype.toString.call(e) === "[object String]";
}
function re(e, t) {
	if (I(e) && I(t)) {
		let n = t;
		for (let [t, r] of Object.entries(e)) t !== "__proto__" && t !== "constructor" && t !== "prototype" && (n[t] = n[t] ? re(r, n[t]) : r);
	} else te(e) && te(t) && t.push(...e);
	return t;
}
function R(e) {
	setTimeout(() => {
		e();
	}, 0);
}
function z(e) {
	let t = [
		"零",
		"一",
		"二",
		"三",
		"四",
		"五",
		"六",
		"七",
		"八",
		"九"
	], n = [
		"",
		"十",
		"百",
		"千",
		"万",
		"十",
		"百",
		"千",
		"亿",
		"十",
		"百",
		"千",
		"万",
		"十",
		"百",
		"千",
		"亿"
	];
	if (!e || isNaN(e)) return "零";
	let r = e.toString().split(""), i = "";
	for (let e = 0; e < r.length; e++) {
		let a = r.length - 1 - e;
		i = `${n[e]}${i}`, i = `${t[Number(r[a])]}${i}`;
	}
	return i = i.replace(/零(千|百|十)/g, "零").replace(/十零/g, "十"), i = i.replace(/零+/g, "零"), i = i.replace(/零亿/g, "亿").replace(/零万/g, "万"), i = i.replace(/亿万/g, "亿"), i = i.replace(/零+$/, ""), i = i.replace(/^一十/g, "十"), i;
}
function B(e, t, n) {
	for (let r = 0; r < e.length; r++) {
		let i = e[r], a = t[i];
		a === void 0 ? delete n[i] : n[i] = a;
	}
}
function ie(e, t) {
	if (!(!t.length || !e.length)) for (let n = e.length - 1; n >= 0; n--) t.includes(e[n]) && e.splice(n, 1);
}
function V(e, t) {
	let n = {};
	for (let r in e) t.includes(r) && (n[r] = e[r]);
	return n;
}
function ae(e, t) {
	let n = {};
	for (let r in e) t.includes(r) || (n[r] = e[r]);
	return n;
}
function oe(e) {
	let t = new TextEncoder().encode(e), n = Array.from(t, (e) => String.fromCharCode(e));
	return window.btoa(n.join(""));
}
function se(e) {
	let t = e.parentElement;
	for (; t;) {
		let e = window.getComputedStyle(t).getPropertyValue("overflow-y");
		if (t.scrollHeight > t.clientHeight && (e === "auto" || e === "scroll")) return t;
		t = t.parentElement;
	}
	return document.documentElement;
}
function ce(e, t) {
	return e.length === t.length && !e.some((e) => !t.includes(e));
}
function le(e, t) {
	if (!I(e) || !I(t)) return !1;
	let n = Object.keys(e), r = Object.keys(t);
	return n.length === r.length && !n.some((n) => t[n] !== e[n]);
}
function ue(e, t) {
	let n = e.x, r = e.x + e.width, i = e.y, a = e.y + e.height, o = t.x, s = t.x + t.width, c = t.y, l = t.y + t.height;
	return !(n > s || r < o || i > l || a < c);
}
function de(e) {
	return e == null;
}
function fe(e) {
	return new Promise((t, n) => {
		let r = new Image();
		r.onload = () => t(r), r.onerror = n, r.src = e;
	});
}
function pe(e) {
	return e.replace(/\r\n|\r/g, "\n");
}
function me(e, t, n = 0) {
	let r = Math.max(0, Math.floor(n));
	if (r >= e.length) return typeof t == "string" && t === "" ? {
		index: e.length,
		length: 0
	} : {
		index: -1,
		length: 0
	};
	if (typeof t == "string") {
		if (t === "") return {
			index: r,
			length: 0
		};
		let n = e.indexOf(t, r);
		return n === -1 ? {
			index: -1,
			length: 0
		} : {
			index: n,
			length: t.length
		};
	}
	let i = t.flags, a = i.includes("g") ? i : i + "g", o = new RegExp(t.source, a);
	o.lastIndex = r;
	let s = o.exec(e);
	return s ? {
		index: s.index,
		length: s[0].length
	} : {
		index: -1,
		length: 0
	};
}
function he(e, t) {
	if (!t) {
		e.scrollTop = 0;
		return;
	}
	let n = [], r = t.offsetParent;
	for (; r && e !== r && e.contains(r);) n.push(r), r = r.offsetParent;
	let i = t.offsetTop + n.reduce((e, t) => e + t.offsetTop, 0), a = i + t.offsetHeight, o = e.scrollTop, s = o + e.clientHeight;
	i < o ? e.scrollTop = i : a > s && (e.scrollTop = a - e.clientHeight);
}
//#endregion
//#region src/editor/dataset/constant/Cursor.ts
var ge = {
	width: 1,
	color: "#000000",
	dragWidth: 2,
	dragColor: "#0000FF",
	dragFloatImageDisabled: !1
}, _e = "editor-component", ve = "ce-clipboard", ye = {
	print: {
		imagePreviewerDisabled: !1,
		backgroundDisabled: !1,
		filterEmptyControl: !0,
		areaHideDisabled: !1
	},
	readonly: { imagePreviewerDisabled: !1 },
	form: { controlDeletableDisabled: !1 }
}, be;
(function(e) {
	e.UP = "top", e.DOWN = "down", e.LEFT = "left", e.RIGHT = "right";
})(be ||= {});
//#endregion
//#region src/editor/utils/ua.ts
var xe = typeof navigator < "u" && /Mac OS X/.test(navigator.userAgent), Se = typeof navigator < "u" && /iPad|iPhone/.test(navigator.userAgent), Ce = /Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent), we = typeof navigator < "u" && /Firefox/.test(navigator.userAgent), H;
(function(e) {
	e.TEXT = "text", e.IMAGE = "image", e.TABLE = "table", e.HYPERLINK = "hyperlink", e.SUPERSCRIPT = "superscript", e.SUBSCRIPT = "subscript", e.SEPARATOR = "separator", e.PAGE_BREAK = "pageBreak", e.CONTROL = "control", e.AREA = "area", e.CHECKBOX = "checkbox", e.RADIO = "radio", e.LATEX = "latex", e.TAB = "tab", e.DATE = "date", e.BLOCK = "block", e.TITLE = "title", e.LIST = "list", e.LABEL = "label";
})(H ||= {});
//#endregion
//#region src/editor/dataset/constant/Element.ts
var Te = [
	"bold",
	"color",
	"highlight",
	"font",
	"size",
	"italic",
	"underline",
	"strikeout",
	"textDecoration"
], Ee = ["rowFlex", "rowMargin"], De = ["trace"], Oe = ["hint"], ke = [
	"rowFlex",
	"rowMargin",
	"level",
	"title"
], Ae = [
	"type",
	"font",
	"size",
	"bold",
	"color",
	"italic",
	"highlight",
	"underline",
	"strikeout",
	"rowFlex",
	"url",
	"areaId",
	"hyperlinkId",
	"dateId",
	"dateFormat",
	"groupIds",
	"rowMargin",
	"textDecoration"
], je = /* @__PURE__ */ "type.font.size.bold.color.italic.highlight.underline.strikeout.rowFlex.rowMargin.dashArray.trList.tableToolDisabled.borderType.borderColor.translateX.width.height.url.colgroup.valueList.control.checkbox.radio.dateFormat.block.level.title.listType.listStyle.listWrap.listLevel.groupIds.conceptId.imgDisplay.imgFloatPosition.imgToolDisabled.imgPreviewDisabled.imgCrop.imgCaption.textDecoration.extension.externalId.areaId.area.hide.label.labelId.lineWidth.trace.paperDirection.hint".split("."), Me = [
	"conceptId",
	"extension",
	"externalId",
	"verticalAlign",
	"backgroundColor",
	"borderTypes",
	"slashTypes",
	"disabled",
	"deletable"
], Ne = [
	"tdId",
	"trId",
	"tableId"
], Pe = [
	"level",
	"titleId",
	"title"
], Fe = [
	"listId",
	"listType",
	"listStyle",
	"listLevel"
], Ie = [
	"control",
	"controlId",
	"controlComponent"
], Le = [
	"font",
	"size",
	"bold",
	"highlight",
	"italic",
	"strikeout"
], Re = ["areaId", "area"], ze = [
	...Ne,
	...Pe,
	...Fe,
	...Re
], Be = [
	H.TEXT,
	H.HYPERLINK,
	H.SUBSCRIPT,
	H.SUPERSCRIPT,
	H.CONTROL,
	H.DATE
], Ve = [H.IMAGE, H.LATEX], He = [
	H.BLOCK,
	H.PAGE_BREAK,
	H.SEPARATOR,
	H.TABLE
], Ue = [
	"HR",
	"TABLE",
	"UL",
	"OL"
], We = [H.TITLE, H.LIST], Ge = class e {
	static sandbox = ["allow-scripts", "allow-same-origin"];
	static allow = ["fullscreen"];
	element;
	iframe = null;
	isReadonly;
	constructor(e) {
		this.element = e, this.isReadonly = !1;
	}
	getIframe() {
		return this.iframe;
	}
	_defineIframeProperties(e) {
		Object.defineProperties(e, {
			parent: { get: () => null },
			__POWERED_BY_CANVAS_EDITOR__: { get: () => !0 }
		});
	}
	render(t) {
		let { iframeBlock: n } = this.element.block || {}, r = document.createElement("iframe");
		r.setAttribute("data-id", this.element.id), r.sandbox.add(...n?.sandbox || e.sandbox), r.setAttribute("allow", [n?.allow || e.allow].join(" ")), r.style.border = "none", r.style.width = "100%", r.style.height = "100%", n?.src ? r.src = n.src : n?.srcdoc && (r.srcdoc = n.srcdoc), t.append(r), this._defineIframeProperties(r.contentWindow), this.iframe = r;
	}
	setReadonly(e) {
		!this.iframe || this.isReadonly === e || (this.isReadonly = e, e ? (this.iframe.style.pointerEvents = "none", this.iframe.setAttribute("tabindex", "-1")) : (this.iframe.style.pointerEvents = "", this.iframe.removeAttribute("tabindex")));
	}
}, Ke = class {
	draw;
	options;
	imageCache;
	container;
	floatImageContainer;
	floatImage;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer(), this.imageCache = /* @__PURE__ */ new Map(), this.floatImageContainer = null, this.floatImage = null;
	}
	getOriginalMainImageList() {
		let e = [], t = (n) => {
			for (let r of n) if (r.type === H.TABLE) {
				let e = r.trList;
				for (let n = 0; n < e.length; n++) {
					let r = e[n];
					for (let e = 0; e < r.tdList.length; e++) {
						let n = r.tdList[e];
						t(n.value);
					}
				}
			} else r.type === H.IMAGE && e.push(r);
		};
		return t(this.draw.getOriginalMainElementList()), e;
	}
	_countImagesBeforeTarget(e, t) {
		let n = 0;
		for (let r of e) {
			if (r === t) break;
			if (r.type === H.TABLE) {
				let e = r.trList;
				for (let r of e) for (let e of r.tdList) n += this._countImagesBeforeTarget(e.value, t);
			} else r.type === H.IMAGE && n++;
		}
		return n;
	}
	createFloatImage(e) {
		let { scale: t } = this.options, n = this.floatImageContainer, r = this.floatImage;
		n || (n = document.createElement("div"), n.classList.add("ce-float-image"), this.container.append(n), this.floatImageContainer = n), r || (r = document.createElement("img"), n.append(r), this.floatImage = r), n.style.display = "none", r.style.width = `${e.width * t}px`, r.style.height = `${e.height * t}px`;
		let { x: i, y: a } = this.draw.getPageOffset(this.draw.getPageNo()), o = this.draw.getPosition(), s = o.getFloatPositionByElement(e);
		if (!s) return;
		let { x: c, y: l } = o.getFloatPositionCoordinate(s);
		n.style.left = `${c + i}px`, n.style.top = `${a + l}px`, r.src = e.value;
	}
	dragFloatImage(e, t) {
		if (!this.floatImageContainer) return;
		this.floatImageContainer.style.display = "block";
		let n = parseFloat(this.floatImageContainer.style.left) + e, r = parseFloat(this.floatImageContainer.style.top) + t;
		this.floatImageContainer.style.left = `${n}px`, this.floatImageContainer.style.top = `${r}px`;
	}
	destroyFloatImage() {
		this.floatImageContainer && (this.floatImageContainer.style.display = "none");
	}
	addImageObserver(e) {
		this.draw.getImageObserver().add(e);
	}
	getFallbackImage(e, t) {
		let n = `<svg xmlns="http://www.w3.org/2000/svg" width="${e}" height="${t}" viewBox="0 0 ${e} ${t}">
                  <rect width="${e}" height="${t}" fill="url(#mosaic)" />
                  <defs>
                    <pattern id="mosaic" x="${(e - Math.ceil(e / 8) * 8) / 2}" y="${(t - Math.ceil(t / 8) * 8) / 2}" width="16" height="16" patternUnits="userSpaceOnUse">
                      <rect width="8" height="8" fill="#cccccc" />
                      <rect width="8" height="8" fill="#cccccc" transform="translate(8, 8)" />
                    </pattern>
                  </defs>
                </svg>`, r = new Image();
		return r.src = `data:image/svg+xml;base64,${oe(n)}`, r;
	}
	_drawImageWithCrop(e, t, n, r, i, a, o) {
		if (n.imgCrop) {
			let { x: s, y: c, width: l, height: u } = n.imgCrop;
			e.drawImage(t, s, c, l, u, r, i, a, o);
		} else e.drawImage(t, r, i, a, o);
	}
	_renderCaption(e, t, n, r, i, a) {
		if (!t.imgCaption?.value) return;
		let { scale: o, imgCaption: s } = this.options, c = t.imgCaption.value;
		if (c.includes("{imageNo}")) {
			let e = this.draw.getOriginalMainElementList(), n = this._countImagesBeforeTarget(e, t) + 1;
			c = c.replace(/\{imageNo\}/g, String(n));
		}
		let l = (t.imgCaption.size || s.size) * o, u = t.imgCaption.font || s.font, d = t.imgCaption.color || s.color;
		e.save(), e.font = `${l}px ${u}`, e.fillStyle = d, e.textAlign = "center";
		let f = c, p = e.measureText(c);
		if (p.width > i) {
			let t = 0, n = c.length;
			for (; t < n;) {
				let r = Math.ceil((t + n) / 2), a = c.substring(0, r);
				e.measureText(a + "...").width <= i ? t = r : n = r - 1;
			}
			f = c.substring(0, t) + "...";
		}
		let m = (t.imgCaption.top ?? s.top) * o, h = r + a + m + p.actualBoundingBoxAscent, g = n + i / 2;
		e.fillText(f, g, h), e.restore();
	}
	render(e, t, n, i) {
		let { scale: a } = this.options, o = t.width * a, s = t.height * a;
		if (this.imageCache.has(t.value)) {
			let r = this.imageCache.get(t.value);
			this._drawImageWithCrop(e, r, t, n, i, o, s), this._renderCaption(e, t, n, i, o, s);
		} else {
			let a = this.draw.getRenderCount(), c = new Promise((c, l) => {
				let u = new Image();
				u.setAttribute("crossOrigin", "Anonymous"), u.src = t.value, u.onload = () => {
					this.imageCache.set(t.value, u), c(t), a === this.draw.getRenderCount() && (t.imgDisplay === r.FLOAT_BOTTOM ? this.draw.render({
						isCompute: !1,
						isSetCursor: !1,
						isSubmitHistory: !1
					}) : (this._drawImageWithCrop(e, u, t, n, i, o, s), this._renderCaption(e, t, n, i, o, s)));
				}, u.onerror = (r) => {
					let a = this.getFallbackImage(o, s);
					a.onload = () => {
						this._drawImageWithCrop(e, a, t, n, i, o, s), this.imageCache.set(t.value, a), this._renderCaption(e, t, n, i, o, s);
					}, l(r);
				};
			});
			this.addImageObserver(c);
		}
	}
}, qe = 82;
function Je(e) {
	return Xe[e] ?? Ye(e), Xe[e];
}
function Ye(e) {
	let t = Ze[e];
	if (t == null) return;
	let n = t.substring(3, 5), r = 1 * n.charCodeAt(0) - qe, i = 1 * n.charCodeAt(1) - qe, a = t.substring(5), o = [[]], s = Infinity, c = -Infinity, l = Infinity, u = -Infinity, d = 0;
	for (; d < a.length;) {
		let e = a.substring(d, d + 2);
		if (e == " R") o.push([]);
		else {
			let t = e.charCodeAt(0) - qe - r, n = e.charCodeAt(1) - qe;
			s = Math.min(n, s), c = Math.max(n, c), l = Math.min(t, l), u = Math.max(t, u), o[o.length - 1].push([t, n]);
		}
		d += 2;
	}
	Xe[e] = {
		w: i - r,
		xmin: l,
		xmax: u,
		ymin: s,
		ymax: c,
		polylines: o
	};
}
var Xe = {}, Ze = {
	1: "  9MWRMNV RRMVV RPSTS",
	2: " 16MWOMOV ROMSMUNUPSQ ROQSQURUUSVOV",
	3: " 11MXVNTMRMPNOPOSPURVTVVU",
	4: " 12MWOMOV ROMRMTNUPUSTURVOV",
	5: " 12MWOMOV ROMUM ROQSQ ROVUV",
	6: "  9MVOMOV ROMUM ROQSQ",
	7: " 15MXVNTMRMPNOPOSPURVTVVUVR RSRVR",
	8: "  9MWOMOV RUMUV ROQUQ",
	9: "  3PTRMRV",
	10: "  7NUSMSTRVPVOTOS",
	11: "  9MWOMOV RUMOS RQQUV",
	12: "  6MVOMOV ROVUV",
	13: " 12LXNMNV RNMRV RVMRV RVMVV",
	14: "  9MWOMOV ROMUV RUMUV",
	15: " 14MXRMPNOPOSPURVSVUUVSVPUNSMRM",
	16: " 10MWOMOV ROMSMUNUQSROR",
	17: " 17MXRMPNOPOSPURVSVUUVSVPUNSMRM RSTVW",
	18: " 13MWOMOV ROMSMUNUQSROR RRRUV",
	19: " 13MWUNSMQMONOOPPTRUSUUSVQVOU",
	20: "  6MWRMRV RNMVM",
	21: "  9MXOMOSPURVSVUUVSVM",
	22: "  6MWNMRV RVMRV",
	23: " 12LXNMPV RRMPV RRMTV RVMTV",
	24: "  6MWOMUV RUMOV",
	25: "  7MWNMRQRV RVMRQ",
	26: "  9MWUMOV ROMUM ROVUV",
	27: "  9MWRMNV RRMVV RPSTS",
	28: " 16MWOMOV ROMSMUNUPSQ ROQSQURUUSVOV",
	29: "  6MVOMOV ROMUM",
	30: "  9MWRMNV RRMVV RNVVV",
	31: " 12MWOMOV ROMUM ROQSQ ROVUV",
	32: "  9MWUMOV ROMUM ROVUV",
	33: "  9MWOMOV RUMUV ROQUQ",
	34: " 20MXRMPNOPOSPURVSVUUVSVPUNSMRM RQQTR RTQQR",
	35: "  3PTRMRV",
	36: "  9MWOMOV RUMOS RQQUV",
	37: "  6MWRMNV RRMVV",
	38: " 12LXNMNV RNMRV RVMRV RVMVV",
	39: "  9MWOMOV ROMUV RUMUV",
	40: " 12MWOMUM RPQTR RTQPR ROVUV",
	41: " 14MXRMPNOPOSPURVSVUUVSVPUNSMRM",
	42: "  9MWOMOV RUMUV ROMUM",
	43: " 10MWOMOV ROMSMUNUQSROR",
	44: " 10MWOMRQOV ROMUM ROVUV",
	45: "  6MWRMRV RNMVM",
	46: " 15MWNONNOMPMQNRPRV RVOVNUMTMSNRP",
	47: " 13LXRMRV RPONPNSPTTTVSVPTOPO",
	48: "  6MWOMUV RUMOV",
	49: " 12LXRMRV RNOOPOSQTSTUSUPVO",
	50: " 13MXOVQVOROPPNRMSMUNVPVRTVVV",
	200: " 12MWRMPNOPOSPURVTUUSUPTNRM",
	201: "  4MWPORMRV",
	202: "  9MWONQMSMUNUPTROVUV",
	203: " 15MWONQMSMUNUPSQ RRQSQURUUSVQVOU",
	204: "  7MWSMSV RSMNSVS",
	205: " 14MWPMOQQPRPTQUSTURVQVOU RPMTM",
	206: " 14MWTMRMPNOPOSPURVTUUSTQRPPQOS",
	207: "  6MWUMQV ROMUM",
	208: " 19MWQMONOPQQSQUPUNSMQM RQQOROUQVSVUUURSQ",
	209: " 14MWUPTRRSPROPPNRMTNUPUSTURVPV",
	210: "  6PURURVSVSURU",
	211: "  7PUSVRVRUSUSWRY",
	212: " 12PURPRQSQSPRP RRURVSVSURU",
	213: " 13PURPRQSQSPRP RSVRVRUSUSWRY",
	214: " 12PURMRR RSMSR RRURVSVSURU",
	215: " 17NWPNRMSMUNUPRQRRSRSQUP RRURVSVSURU",
	216: "  3PTRMRQ",
	217: "  6NVPMPQ RTMTQ",
	218: " 10NVQMPNPPQQSQTPTNSMQM",
	219: " 16MWUNSMQMONOPQQTRUSUUSVQVOU RRLRW",
	220: "  3MWVLNW",
	221: "  7OVTLRNQPQSRUTW",
	222: "  7NUPLRNSPSSRUPW",
	223: "  3PTRLRW",
	224: "  3LXNRVR",
	225: "  6LXRNRV RNRVR",
	226: "  6LXNPVP RNTVT",
	227: "  6MWOOUU RUOOU",
	228: "  9MWRORU ROPUT RUPOT",
	229: "  6PURQRRSRSQRQ",
	230: "  7PUSMRORQSQSPRP",
	231: "  7PUSNRNRMSMSORQ",
	232: "  7LXSOVRSU RNRVR",
	233: " 12MXRLPW RULSW ROPVP ROSVS",
	234: " 21LXVRURTSSURVOVNUNSORRQSPSNRMPMONOPQSSUUVVV",
	235: " 20LXNNOQOSNV RVNUQUSVV RNNQOSOVN RNVQUSUVV",
	501: "  9I[RFJ[ RRFZ[ RMTWT",
	502: " 24G\\KFK[ RKFTFWGXHYJYLXNWOTP RKPTPWQXRYTYWXYWZT[K[",
	503: " 19H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZV",
	504: " 16G\\KFK[ RKFRFUGWIXKYNYSXVWXUZR[K[",
	505: " 12H[LFL[ RLFYF RLPTP RL[Y[",
	506: "  9HZLFL[ RLFYF RLPTP",
	507: " 23H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZVZS RUSZS",
	508: "  9G]KFK[ RYFY[ RKPYP",
	509: "  3NVRFR[",
	510: " 11JZVFVVUYTZR[P[NZMYLVLT",
	511: "  9G\\KFK[ RYFKT RPOY[",
	512: "  6HYLFL[ RL[X[",
	513: " 12F^JFJ[ RJFR[ RZFR[ RZFZ[",
	514: "  9G]KFK[ RKFY[ RYFY[",
	515: " 22G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF",
	516: " 14G\\KFK[ RKFTFWGXHYJYMXOWPTQKQ",
	517: " 25G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF RSWY]",
	518: " 17G\\KFK[ RKFTFWGXHYJYLXNWOTPKP RRPY[",
	519: " 21H\\YIWGTFPFMGKIKKLMMNOOUQWRXSYUYXWZT[P[MZKX",
	520: "  6JZRFR[ RKFYF",
	521: " 11G]KFKULXNZQ[S[VZXXYUYF",
	522: "  6I[JFR[ RZFR[",
	523: " 12F^HFM[ RRFM[ RRFW[ R\\FW[",
	524: "  6H\\KFY[ RYFK[",
	525: "  7I[JFRPR[ RZFRP",
	526: "  9H\\YFK[ RKFYF RK[Y[",
	527: "  9I[RFJ[ RRFZ[ RMTWT",
	528: " 24G\\KFK[ RKFTFWGXHYJYLXNWOTP RKPTPWQXRYTYWXYWZT[K[",
	529: "  6HYLFL[ RLFXF",
	530: "  9I[RFJ[ RRFZ[ RJ[Z[",
	531: " 12H[LFL[ RLFYF RLPTP RL[Y[",
	532: "  9H\\YFK[ RKFYF RK[Y[",
	533: "  9G]KFK[ RYFY[ RKPYP",
	534: " 25G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF ROPUP",
	535: "  3NVRFR[",
	536: "  9G\\KFK[ RYFKT RPOY[",
	537: "  6I[RFJ[ RRFZ[",
	538: " 12F^JFJ[ RJFR[ RZFR[ RZFZ[",
	539: "  9G]KFK[ RKFY[ RYFY[",
	540: "  9I[KFYF ROPUP RK[Y[",
	541: " 22G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF",
	542: "  9G]KFK[ RYFY[ RKFYF",
	543: " 14G\\KFK[ RKFTFWGXHYJYMXOWPTQKQ",
	544: " 10I[KFRPK[ RKFYF RK[Y[",
	545: "  6JZRFR[ RKFYF",
	546: " 19I[KKKILGMFOFPGQIRMR[ RYKYIXGWFUFTGSIRM",
	547: " 21H\\RFR[ RPKMLLMKOKRLTMUPVTVWUXTYRYOXMWLTKPK",
	548: "  6H\\KFY[ RK[YF",
	549: " 18G]RFR[ RILJLKMLQMSNTQUSUVTWSXQYMZL[L",
	550: " 17H\\K[O[LTKPKLLINGQFSFVGXIYLYPXTU[Y[",
	551: " 20G[G[IZLWOSSLVFV[UXSUQSNQLQKRKTLVNXQZT[Y[",
	552: " 41F]SHTITLSPRSQUOXMZK[J[IZIWJRKOLMNJPHRGUFXFZG[I[KZMYNWOTP RSPTPWQXRYTYWXYWZU[R[PZOX",
	553: " 24H\\TLTMUNWNYMZKZIYGWFTFQGOIMLLNKRKVLYMZO[Q[TZVXWV",
	554: " 35G^TFRGQIPMOSNVMXKZI[G[FZFXGWIWKXMZP[S[VZXXZT[O[KZHYGWFTFRHRJSMUPWRZT\\U",
	555: " 28H\\VJVKWLYLZKZIYGVFRFOGNINLONPOSPPPMQLRKTKWLYMZP[S[VZXXYV",
	556: " 28H\\RLPLNKMINGQFTFXG[G]F RXGVNTTRXPZN[L[JZIXIVJULUNV RQPZP",
	557: " 29G^G[IZMVPQQNRJRGQFPFOGNINLONQOUOXNYMZKZQYVXXVZS[O[LZJXIVIT",
	558: " 38F^MMKLJJJIKGMFNFPGQIQKPONULYJ[H[GZGX RMRVOXN[L]J^H^G]F\\FZHXLVRUWUZV[W[YZZY\\V",
	559: " 25IZWVUTSQROQLQIRGSFUFVGWIWLVQTVSXQZO[M[KZJXJVKUMUOV",
	560: " 25JYT^R[PVOPOJPGRFTFUGVJVMURR[PaOdNfLgKfKdLaN^P\\SZWX",
	561: " 39F^MMKLJJJIKGMFNFPGQIQKPONULYJ[H[GZGX R^I^G]F\\FZGXIVLTNROPO RROSQSXTZU[V[XZYY[V",
	562: " 29I\\MRORSQVOXMYKYHXFVFUGTISNRSQVPXNZL[J[IZIXJWLWNXQZT[V[YZ[X",
	563: " 45@aEMCLBJBICGEFFFHGIIIKHPGTE[ RGTJLLHMGOFPFRGSISKRPQTO[ RQTTLVHWGYFZF\\G]I]K\\PZWZZ[[\\[^Z_YaV",
	564: " 32E]JMHLGJGIHGJFKFMGNINKMPLTJ[ RLTOLQHRGTFVFXGYIYKXPVWVZW[X[ZZ[Y]V",
	565: " 29H]TFQGOIMLLNKRKVLYMZO[Q[TZVXXUYSZOZKYHXGVFTFRHRKSNUQWSZU\\V",
	566: " 31F_SHTITLSPRSQUOXMZK[J[IZIWJRKOLMNJPHRGUFZF\\G]H^J^M]O\\PZQWQUPTO",
	567: " 32H^ULTNSOQPOPNNNLOIQGTFWFYGZIZMYPWSSWPYNZK[I[HZHXIWKWMXPZS[V[YZ[X",
	568: " 38F_SHTITLSPRSQUOXMZK[J[IZIWJRKOLMNJPHRGUFYF[G\\H]J]M\\O[PYQVQSPTQUSUXVZX[ZZ[Y]V",
	569: " 28H\\H[JZLXOTQQSMTJTGSFRFQGPIPKQMSOVQXSYUYWXYWZT[P[MZKXJVJT",
	570: " 25H[RLPLNKMINGQFTFXG[G]F RXGVNTTRXPZN[L[JZIXIVJULUNV",
	571: " 33E]JMHLGJGIHGJFKFMGNINKMOLRKVKXLZN[P[RZSYUUXMZF RXMWQVWVZW[X[ZZ[Y]V",
	572: " 32F]KMILHJHIIGKFLFNGOIOKNOMRLVLYM[O[QZTWVTXPYMZIZGYFXFWGVIVKWNYP[Q",
	573: " 25C_HMFLEJEIFGHFIFKGLILLK[ RUFK[ RUFS[ RaF_G\\JYNVTS[",
	574: " 36F^NLLLKKKILGNFPFRGSISLQUQXRZT[V[XZYXYVXUVU R]I]G\\FZFXGVITLPUNXLZJ[H[GZGX",
	575: " 38F]KMILHJHIIGKFLFNGOIOKNOMRLVLXMZN[P[RZTXVUWSYM R[FYMVWT]RbPfNgMfMdNaP^S[VY[V",
	576: " 40H]ULTNSOQPOPNNNLOIQGTFWFYGZIZMYPWTTWPZN[K[JZJXKWNWPXQYR[R^QaPcNfLgKfKdLaN^Q[TYZV",
	583: "  9I[JFR[ RZFR[ RJFZF",
	601: " 18I\\XMX[ RXPVNTMQMONMPLSLUMXOZQ[T[VZXX",
	602: " 18H[LFL[ RLPNNPMSMUNWPXSXUWXUZS[P[NZLX",
	603: " 15I[XPVNTMQMONMPLSLUMXOZQ[T[VZXX",
	604: " 18I\\XFX[ RXPVNTMQMONMPLSLUMXOZQ[T[VZXX",
	605: " 18I[LSXSXQWOVNTMQMONMPLSLUMXOZQ[T[VZXX",
	606: "  9MYWFUFSGRJR[ ROMVM",
	607: " 23I\\XMX]W`VaTbQbOa RXPVNTMQMONMPLSLUMXOZQ[T[VZXX",
	608: " 11I\\MFM[ RMQPNRMUMWNXQX[",
	609: "  9NVQFRGSFREQF RRMR[",
	610: " 12MWRFSGTFSERF RSMS^RaPbNb",
	611: "  9IZMFM[ RWMMW RQSX[",
	612: "  3NVRFR[",
	613: " 19CaGMG[ RGQJNLMOMQNRQR[ RRQUNWMZM\\N]Q][",
	614: " 11I\\MMM[ RMQPNRMUMWNXQX[",
	615: " 18I\\QMONMPLSLUMXOZQ[T[VZXXYUYSXPVNTMQM",
	616: " 18H[LMLb RLPNNPMSMUNWPXSXUWXUZS[P[NZLX",
	617: " 18I\\XMXb RXPVNTMQMONMPLSLUMXOZQ[T[VZXX",
	618: "  9KXOMO[ ROSPPRNTMWM",
	619: " 18J[XPWNTMQMNNMPNRPSUTWUXWXXWZT[Q[NZMX",
	620: "  9MYRFRWSZU[W[ ROMVM",
	621: " 11I\\MMMWNZP[S[UZXW RXMX[",
	622: "  6JZLMR[ RXMR[",
	623: " 12G]JMN[ RRMN[ RRMV[ RZMV[",
	624: "  6J[MMX[ RXMM[",
	625: " 10JZLMR[ RXMR[P_NaLbKb",
	626: "  9J[XMM[ RMMXM RM[X[",
	627: " 24H]QMONMPLRKUKXLZN[P[RZUWWTYPZM RQMSMTNUPWXXZY[Z[",
	628: " 31I\\UFSGQIOMNPMTLZKb RUFWFYHYKXMWNUORO RROTPVRWTWWVYUZS[Q[OZNYMV",
	629: " 17I\\JPLNNMOMQNROSRSVR[ RZMYPXRR[P_Ob",
	630: " 24I[TMQMONMPLSLVMYNZP[R[TZVXWUWRVOTMRKQIQGRFTFVGXI",
	631: " 19JZWOVNTMQMONOPPRSS RSSOTMVMXNZP[S[UZWX",
	632: " 23JYTFRGQHQIRJUKXK RXKTMQONRMUMWNYP[S]T_TaSbQbP`",
	633: " 19H\\IQJOLMNMONOPNTL[ RNTPPRNTMVMXOXRWWTb",
	634: " 27G\\HQIOKMMMNNNPMUMXNZO[Q[SZUWVUWRXMXJWGUFSFRHRJSMUPWRZT",
	635: "  9LWRMPTOXOZP[R[TYUW",
	636: " 19I[OMK[ RYNXMWMUNQROSNS RNSPTQUSZT[U[VZ",
	637: "  9JZKFMFOGPHX[ RRML[",
	638: " 21H]OMIb RNQMVMYO[Q[SZUXWT RYMWTVXVZW[Y[[Y\\W",
	639: " 14I[LMOMNSMXL[ RYMXPWRUURXOZL[",
	640: " 29JZTFRGQHQIRJUKXK RUKRLPMOOOQQSTTVT RTTPUNVMXMZO\\S^T_TaRbPb",
	641: " 18J[RMPNNPMSMVNYOZQ[S[UZWXXUXRWOVNTMRM",
	642: " 13G]PML[ RUMVSWXX[ RIPKNNM[M",
	643: " 19I[MSMVNYOZQ[S[UZWXXUXRWOVNTMRMPNNPMSIb",
	644: " 18I][MQMONMPLSLVMYNZP[R[TZVXWUWRVOUNSM",
	645: "  8H\\SMP[ RJPLNOMZM",
	646: " 16H\\IQJOLMNMONOPMVMYO[Q[TZVXXTYPYM",
	647: " 21G]ONMOKQJTJWKYLZN[Q[TZWXYUZRZOXMVMTORSPXMb",
	648: " 14I[KMMMOOU`WbYb RZMYOWRM]K`Jb",
	649: " 20F]VFNb RGQHOJMLMMNMPLULXMZO[Q[TZVXXUZP[M",
	650: " 23F]NMLNJQITIWJZK[M[OZQW RRSQWRZS[U[WZYWZTZQYNXM",
	651: " 22L\\UUTSRRPRNSMTLVLXMZO[Q[SZTXVRUWUZV[W[YZZY\\V",
	652: " 23M[MVOSRNSLTITGSFQGPIOMNTNZO[P[RZTXUUURVVWWYW[V",
	653: " 14MXTTTSSRQROSNTMVMXNZP[S[VYXV",
	654: " 24L\\UUTSRRPRNSMTLVLXMZO[Q[SZTXZF RVRUWUZV[W[YZZY\\V",
	655: " 17NXOYQXRWSUSSRRQROSNUNXOZQ[S[UZVYXV",
	656: " 24OWOVSQUNVLWIWGVFTGSIQQNZKaJdJfKgMfNcOZP[R[TZUYWV",
	657: " 28L[UUTSRRPRNSMTLVLXMZO[Q[SZTY RVRTYPdOfMgLfLdMaP^S\\U[XY[V",
	658: " 29M\\MVOSRNSLTITGSFQGPIOMNSM[ RM[NXOVQSSRURVSVUUXUZV[W[YZZY\\V",
	659: " 16PWSMSNTNTMSM RPVRRPXPZQ[R[TZUYWV",
	660: " 20PWSMSNTNTMSM RPVRRLdKfIgHfHdIaL^O\\Q[TYWV",
	661: " 33M[MVOSRNSLTITGSFQGPIOMNSM[ RM[NXOVQSSRURVSVUTVQV RQVSWTZU[V[XZYY[V",
	662: " 18OWOVQSTNULVIVGUFSGRIQMPTPZQ[R[TZUYWV",
	663: " 33E^EVGSIRJSJTIXH[ RIXJVLSNRPRQSQTPXO[ RPXQVSSURWRXSXUWXWZX[Y[[Z\\Y^V",
	664: " 23J\\JVLSNROSOTNXM[ RNXOVQSSRURVSVUUXUZV[W[YZZY\\V",
	665: " 23LZRRPRNSMTLVLXMZO[Q[SZTYUWUUTSRRQSQURWTXWXYWZV",
	666: " 24KZKVMSNQMUGg RMUNSPRRRTSUUUWTYSZQ[ RMZO[R[UZWYZV",
	667: " 27L[UUTSRRPRNSMTLVLXMZO[Q[SZ RVRUUSZPaOdOfPgRfScS\\U[XY[V",
	668: " 15MZMVOSPQPSSSTTTVSYSZT[U[WZXYZV",
	669: " 16NYNVPSQQQSSVTXTZR[ RNZP[T[VZWYYV",
	670: " 16OXOVQSSO RVFPXPZQ[S[UZVYXV RPNWN",
	671: " 19L[LVNRLXLZM[O[QZSXUU RVRTXTZU[V[XZYY[V",
	672: " 17L[LVNRMWMZN[O[RZTXUUUR RURVVWWYW[V",
	673: " 25I^LRJTIWIYJ[L[NZPX RRRPXPZQ[S[UZWXXUXR RXRYVZW\\W^V",
	674: " 20JZJVLSNRPRQSQZR[U[XYZV RWSVRTRSSOZN[L[KZ",
	675: " 23L[LVNRLXLZM[O[QZSXUU RVRPdOfMgLfLdMaP^S\\U[XY[V",
	676: " 23LZLVNSPRRRTTTVSXQZN[P\\Q^QaPdOfMgLfLdMaP^S\\WYZV",
	677: " 22J\\K[NZQXSVUSWOXKXIWGUFSGRHQJPOPTQXRZT[V[XZYY",
	683: " 26I[WUWRVOUNSMQMONMPLSLVMYNZP[R[TZVXWUXPXKWHVGTFRFPGNI",
	684: " 16JZWNUMRMPNNPMSMVNYOZQ[T[VZ RMTUT",
	685: " 23J[TFRGPJOLNOMTMXNZO[Q[SZUWVUWRXMXIWGVFTF RNPWP",
	686: " 21H\\VFNb RQMNNLPKSKVLXNZQ[S[VZXXYUYRXPVNSMQM",
	687: " 16I[XOWNTMQMNNMOLQLSMUOWSZT\\T^S_Q_",
	700: " 18H\\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF",
	701: "  5H\\NJPISFS[",
	702: " 15H\\LKLJMHNGPFTFVGWHXJXLWNUQK[Y[",
	703: " 16H\\MFXFRNUNWOXPYSYUXXVZS[P[MZLYKW",
	704: "  7H\\UFKTZT RUFU[",
	705: " 18H\\WFMFLOMNPMSMVNXPYSYUXXVZS[P[MZLYKW",
	706: " 24H\\XIWGTFRFOGMJLOLTMXOZR[S[VZXXYUYTXQVOSNRNOOMQLT",
	707: "  6H\\YFO[ RKFYF",
	708: " 30H\\PFMGLILKMMONSOVPXRYTYWXYWZT[P[MZLYKWKTLRNPQOUNWMXKXIWGTFPF",
	709: " 24H\\XMWPURRSQSNRLPKMKLLINGQFRFUGWIXMXRWWUZR[P[MZLX",
	710: "  6MWRYQZR[SZRY",
	711: "  9MWSZR[QZRYSZS\\R^Q_",
	712: " 12MWRMQNROSNRM RRYQZR[SZRY",
	713: " 15MWRMQNROSNRM RSZR[QZRYSZS\\R^Q_",
	714: "  9MWRFRT RRYQZR[SZRY",
	715: " 21I[LKLJMHNGPFTFVGWHXJXLWNVORQRT RRYQZR[SZRY",
	716: "  3NVRFRM",
	717: "  6JZNFNM RVFVM",
	718: " 14KYQFOGNINKOMQNSNUMVKVIUGSFQF",
	719: " 27H\\PBP_ RTBT_ RYIWGTFPFMGKIKKLMMNOOUQWRXSYUYXWZT[P[MZKX",
	720: "  3G][BIb",
	721: " 11KYVBTDRGPKOPOTPYR]T`Vb",
	722: " 11KYNBPDRGTKUPUTTYR]P`Nb",
	723: "  3NVRBRb",
	724: "  3E_IR[R",
	725: "  6E_RIR[ RIR[R",
	726: "  6E_IO[O RIU[U",
	727: "  6G]KKYY RYKKY",
	728: "  9JZRLRX RMOWU RWOMU",
	729: "  6MWRQQRRSSRRQ",
	730: "  8MWSFRGQIQKRLSKRJ",
	731: "  8MWRHQGRFSGSIRKQL",
	732: "  9E_UMXP[RXTUW RIR[R",
	733: " 12H]SBLb RYBRb RLOZO RKUYU",
	734: " 35E_\\O\\N[MZMYNXPVUTXRZP[L[JZIYHWHUISJRQNRMSKSIRGPFNGMIMKNNPQUXWZY[[[\\Z\\Y",
	735: " 28G]IIJKKOKUJYI[ R[IZKYOYUZY[[ RIIKJOKUKYJ[I RI[KZOYUYYZ[[",
	737: "  6KYOBO[ RUBU[",
	738: "  6F^RBR[ RI[[[",
	739: "  4F^[BI[[[",
	740: " 18E_RIQJRKSJRI RIYHZI[JZIY R[YZZ[[\\Z[Y",
	741: " 33F^RHNLKPJSJUKWMXOXQWRU RRHVLYPZSZUYWWXUXSWRU RRUQYP\\ RRUSYT\\ RP\\T\\",
	742: " 26F^RNQKPINHMHKIJKJOKRLTNWR\\ RRNSKTIVHWHYIZKZOYRXTVWR\\",
	743: " 20F^RGPJLOIR RRGTJXO[R RIRLUPZR] R[RXUTZR]",
	744: " 48F^RTTWVXXXZW[U[SZQXPVPSQ RSQUOVMVKUISHQHOINKNMOOQQ RQQNPLPJQISIUJWLXNXPWRT RRTQYP\\ RRTSYT\\ RP\\T\\",
	745: " 55F^RRR[Q\\ RRVQ\\ RRIQHOHNINKONRR RRISHUHVIVKUNRR RRRNOLNJNIOIQJR RRRVOXNZN[O[QZR RRRNULVJVIUISJR RRRVUXVZV[U[SZR",
	746: " 55F^ISJSLTMVMXLZ RISIRJQLQMRNTNWMYLZ RRGPIOLOOQUQXPZR\\ RRGTIULUOSUSXTZR\\ R[S[RZQXQWRVTVWWYXZ R[SZSXTWVWXXZ RKVYV",
	750: " 18PSSRRSQSPRPQQPRPSQSSRUQV RQQQRRRRQQQ",
	751: " 16PTQPPQPSQTSTTSTQSPQP RRQQRRSSRRQ",
	752: "  9NVPOTU RTOPU RNRVR",
	753: " 28MWRKQMOPMR RRKSMUPWR RRMOQ RRMUQ RROPQ RROTQ RQQSQ RMRWR",
	754: " 26MWMRMQNOONQMSMUNVOWQWR RPNTN ROOUO RNPVP RNQVQ RMRWR",
	755: " 14LRLFLRRRLF RLIPQ RLLOR RLOMQ",
	756: " 10MWRKQMOPMR RRKSMUPWR",
	757: " 11MWWRWQVOUNSMQMONNOMQMR",
	758: " 13G]]R]P\\MZJWHTGPGMHJJHMGPGR",
	759: " 11MWMRMSNUOVQWSWUVVUWSWR",
	760: "  7LXLPNRQSSSVRXP",
	761: "  6RURUTTURTPRO",
	762: "  7RVRRUPVNVLUKTK",
	763: "  7NRRROPNNNLOKPK",
	764: " 21MWWHVGTFQFOGNHMJMLNNOOUSVTWVWXVZU[S\\P\\N[MZ",
	765: " 21G]IWHVGTGQHOINKMMMONPOTUUVWWYW[V\\U]S]P\\N[M",
	766: " 31G]RRTUUVWWYW[V\\U]S]Q\\O[NYMWMUNTOPUOVMWKWIVHUGSGQHOINKMMMONPORR",
	767: " 22H\\KFK[ RHF[FQP[Z RZV[Y\\[ RZVZY RWYZY RWYZZ\\[",
	768: " 30KYUARBPCNELHKLKRLUNWQXSXVWXUYR RKPLMNKQJSJVKXMYPYVXZV]T_R`Oa",
	796: "  3>f>RfR",
	797: "  3D`D``D",
	798: "  3RRR>Rf",
	799: "  3D`DD``",
	800: "  3D`DR`R",
	801: "  3F^FY^K",
	802: "  3KYK^YF",
	803: "  3RRRDR`",
	804: "  3KYKFY^",
	805: "  3F^FK^Y",
	806: "  3KYKRYR",
	807: "  3MWMWWM",
	808: "  3RRRKRY",
	809: "  3MWMMWW",
	810: "  8GRRGPGMHJJHMGPGR",
	811: "  8GRGRGTHWJZM\\P]R]",
	812: "  8R]R]T]W\\ZZ\\W]T]R",
	813: "  8R]]R]P\\MZJWHTGRG",
	814: "  9D`DOGQKSPTTTYS]Q`O",
	815: "  9PUUDSGQKPPPTQYS]U`",
	816: "  9OTODQGSKTPTTSYQ]O`",
	817: "  9D`DUGSKQPPTPYQ]S`U",
	818: "  5KYRJYNKVRZ",
	819: "  5JZJRNKVYZR",
	820: "  5KYKVKNYVYN",
	821: "  5JZLXJPZTXL",
	822: " 23JZJ]L]O\\Q[TXUVVSVOULTJSIQIPJOLNONSOVPXS[U\\X]Z]",
	823: " 23I]]Z]X\\U[SXPVOSNONLOJPIQISJTLUOVSVVUXT[Q\\O]L]J",
	824: " 23JZZGXGUHSIPLONNQNUOXPZQ[S[TZUXVUVQUNTLQIOHLGJG",
	825: " 23G[GJGLHOIQLTNUQVUVXUZT[S[QZPXOUNQNNOLPISHUGXGZ",
	826: " 21E[EPFRHTJUMVQVUUXSZP[NZLWLSMQNNPLSKVKYL\\M^",
	827: " 19EYETHVKWPWSVVTXQYNYLXKVKSLPNNQMTMYN\\P_",
	828: " 26OUQOOQOSQUSUUSUQSOQO RQPPQPSQTSTTSTQSPQP RRQQRRSSRRQ",
	829: " 11RWRMSMUNVOWQWSVUUVSWRW",
	830: "  9D`DRJR RORUR RZR`R",
	831: "  5D`DUDO`O`U",
	832: "  6JZRDJR RRDZR",
	833: "  9D`DR`R RJYZY RP`T`",
	834: "  9D`DR`R RDRRb R`RRb",
	840: " 18KYQKNLLNKQKSLVNXQYSYVXXVYSYQXNVLSKQK",
	841: "  6LXLLLXXXXLLL",
	842: "  5KYRJKVYVRJ",
	843: "  6LXRHLRR\\XRRH",
	844: " 12JZRIPOJOOSMYRUWYUSZOTORI",
	845: "  6KYRKRY RKRYR",
	846: "  6MWMMWW RWMMW",
	847: "  9MWRLRX RMOWU RWOMU",
	850: " 35NVQNOONQNSOUQVSVUUVSVQUOSNQN ROQOS RPPPT RQOQU RRORU RSOSU RTPTT RUQUS",
	851: " 27NVNNNVVVVNNN ROOOU RPOPU RQOQU RRORU RSOSU RTOTU RUOUU",
	852: " 17MWRLMUWURL RROOT RROUT RRRQT RRRST",
	853: " 17LULRUWUMLR RORTU RORTO RRRTS RRRTQ",
	854: " 17MWRXWOMORX RRUUP RRUOP RRRSP RRRQP",
	855: " 17OXXROMOWXR RURPO RURPU RRRPQ RRRPS",
	856: " 22LXRLNWXPLPVWRL RRRRL RRRLP RRRNW RRRVW RRRXP",
	857: " 11RYRKRY RRKYNRQ RSMVNSO",
	860: " 13MWRLRX ROOUO RMUOWQXSXUWWU",
	861: " 11LXRLRX RLQMOWOXQ RPWTW",
	862: " 14KYMNWX RWNMX ROLLOKQ RULXOYQ",
	863: " 18I[NII[ RVI[[ RMM[[ RWMI[ RNIVI RMMWM",
	864: " 21I[RGRV RMJWP RWJMP RIVL\\ R[VX\\ RIV[V RL\\X\\",
	865: " 11G[MJSV RKPSL RG\\[\\[RG\\",
	866: " 14LXPLPPLPLTPTPXTXTTXTXPTPTLPL",
	867: " 32KYYPXNVLSKQKNLLNKQKSLVNXQYSYVXXVYT RYPWNUMSMQNPOOQOSPUQVSWUWWVYT",
	868: " 10KYRJKVYVRJ RRZYNKNRZ",
	869: " 34G]PIPGQFSFTGTI RGZHXJVKTLPLKMJOIUIWJXKXPYTZV\\X]Z RGZ]Z RQZP[Q\\S\\T[SZ",
	870: " 64JZRMRS RRSQ\\ RRSS\\ RQ\\S\\ RRMQJPHNG RQJNG RRMSJTHVG RSJVG RRMNKLKJM RPLLLJM RRMVKXKZM RTLXLZM RRMPNOOOR RRMPOOR RRMTNUOUR RRMTOUR",
	871: " 94JZRIRK RRNRP RRSRU RRYQ\\ RRYS\\ RQ\\S\\ RRGQIPJ RRGSITJ RPJRITJ RRKPNNOMN RRKTNVOWN RNOPORNTOVO RRPPSNTLTKRKSLT RRPTSVTXTYRYSXT RNTPTRSTTVT RRUPXOYMZLZKYJWJYLZ RRUTXUYWZXZYYZWZYXZ RMZOZRYUZWZ",
	872: " 40JZRYQ\\ RRYS\\ RQ\\S\\ RRYUZXZZXZUYTWTYRZOYMWLUMVJUHSGQGOHNJOMMLKMJOKRMTKTJUJXLZOZRY",
	873: " 32JZRYQ\\ RRYS\\ RQ\\S\\ RRYVXVVXUXRZQZLYIXHVHTGPGNHLHKIJLJQLRLUNVNXRY",
	874: " 15I[IPKR RLKNP RRGRO RXKVP R[PYR",
	899: "  6QSRQQRRSSRRQ",
	900: " 10PTQPPQPSQTSTTSTQSPQP",
	901: " 14NVQNOONQNSOUQVSVUUVSVQUOSNQN",
	902: " 18MWQMONNOMQMSNUOVQWSWUVVUWSWQVOUNSMQM",
	903: " 18KYQKNLLNKQKSLVNXQYSYVXXVYSYQXNVLSKQK",
	904: " 22G]PGMHJJHMGPGTHWJZM\\P]T]W\\ZZ\\W]T]P\\MZJWHTGPG",
	905: " 34AcPALBJCGEEGCJBLAPATBXCZE]G_JaLbPcTcXbZa]__]aZbXcTcPbLaJ_G]EZCXBTAPA",
	906: " 34<hP<K=G?DAAD?G=K<P<T=Y?]A`DcGeKgPhThYg]e`cc`e]gYhThPgKeGcD`A]?Y=T<P<",
	907: " 50){O)I*E+@-;073370;-@+E*I)O)U*[+_-d0i3m7q;t@wEyIzO{U{[z_ydwitmqqmtiwdy_z[{U{OzIyEw@t;q7m3i0d-_+[*U)O)",
	908: " 34>fRAPCMDJDGCEA>H@JAMAZB]D_G`M`PaRc RRATCWDZD]C_AfHdJcMcZb]`_]`W`TaRc",
	909: " 33AcRAPCMDJDGCEABGAKAPBTDXG\\L`Rc RRATCWDZD]C_AbGcKcPbT`X]\\X`Rc RBHbH",
	997: "  3MWMXWX",
	998: "  3JZJZZZ",
	999: "  3JZJ]Z]",
	1001: " 18KYRKMX RRNVX RRKWX ROTTT RKXPX RTXYX",
	1002: " 35JZNKNX ROKOX RLKSKVLWNVPSQ RSKULVNUPSQ ROQSQVRWTWUVWSXLX RSQURVTVUUWSX",
	1003: " 24KYVLWKWOVLTKQKOLNMMPMSNVOWQXTXVWWU RQKOMNPNSOVQX",
	1004: " 26JZNKNX ROKOX RLKSKVLWMXPXSWVVWSXLX RSKULVMWPWSVVUWSX",
	1005: " 22JYNKNX ROKOX RSOSS RLKVKVOUK ROQSQ RLXVXVTUX",
	1006: " 20JXNKNX ROKOX RSOSS RLKVKVOUK ROQSQ RLXQX",
	1007: " 36K[VLWKWOVLTKQKOLNMMPMSNVOWQXTXVW RQKOMNPNSOVQX RTXUWVU RVSVX RWSWX RTSYS",
	1008: " 27J[NKNX ROKOX RVKVX RWKWX RLKQK RTKYK ROQVQ RLXQX RTXYX",
	1009: " 12NWRKRX RSKSX RPKUK RPXUX",
	1010: " 19LXSKSURWQX RTKTUSWQXPXNWMUNTOUNV RQKVK",
	1011: " 27JZNKNX ROKOX RWKOS RQQVX RRQWX RLKQK RTKYK RLXQX RTXYX",
	1012: " 14KXOKOX RPKPX RMKRK RMXWXWTVX",
	1013: " 30I\\MKMX RNNRX RNKRU RWKRX RWKWX RXKXX RKKNK RWKZK RKXOX RUXZX",
	1014: " 21JZNKNX ROMVX ROKVV RVKVX RLKOK RTKXK RLXPX",
	1015: " 32KZQKOLNMMPMSNVOWQXTXVWWVXSXPWMVLTKQK RQKOMNPNSOVQX RTXVVWSWPVMTK",
	1016: " 25JYNKNX ROKOX RLKSKVLWNWOVQSROR RSKULVNVOUQSR RLXQX",
	1017: " 47KZQKOLNMMPMSNVOWQXTXVWWVXSXPWMVLTKQK RQKOMNPNSOVQX RTXVVWSWPVMTK RPWPUQTSTTUUZV[W[XZ RTUUXVZW[",
	1018: " 37JZNKNX ROKOX RLKSKVLWNWOVQSROR RSKULVNVOUQSR RLXQX RSRTSUWVXWXXW RSRUSVWWX",
	1019: " 32KZVMWKWOVMULSKQKOLNMNOOPQQTRVSWT RNNOOQPTQVRWSWVVWTXRXPWOVNTNXOV",
	1020: " 16KZRKRX RSKSX RNKMOMKXKXOWK RPXUX",
	1021: " 20J[NKNUOWQXTXVWWUWK ROKOUPWQX RLKQK RUKYK",
	1022: " 15KYMKRX RNKRU RWKRX RKKPK RTKYK",
	1023: " 24I[LKOX RMKOT RRKOX RRKUX RSKUT RXKUX RJKOK RVKZK",
	1024: " 21KZNKVX ROKWX RWKNX RLKQK RTKYK RLXQX RTXYX",
	1025: " 20LYNKRRRX ROKSR RWKSRSX RLKQK RTKYK RPXUX",
	1026: " 16LYVKNX RWKOX ROKNONKWK RNXWXWTVX",
	1027: " 18KYRKMX RRNVX RRKWX ROTTT RKXPX RTXYX",
	1028: " 35JZNKNX ROKOX RLKSKVLWNVPSQ RSKULVNUPSQ ROQSQVRWTWUVWSXLX RSQURVTVUUWSX",
	1029: " 14KXOKOX RPKPX RMKWKWOVK RMXRX",
	1030: " 15KYRKLX RRMWX RRKXX RMWVW RLXXX",
	1031: " 22JYNKNX ROKOX RSOSS RLKVKVOUK ROQSQ RLXVXVTUX",
	1032: " 16LYVKNX RWKOX ROKNONKWK RNXWXWTVX",
	1033: " 27J[NKNX ROKOX RVKVX RWKWX RLKQK RTKYK ROQVQ RLXQX RTXYX",
	1034: " 44KZQKOLNMMPMSNVOWQXTXVWWVXSXPWMVLTKQK RQKOMNPNSOVQX RTXVVWSWPVMTK RQOQT RTOTT RQQTQ RQRTR",
	1035: " 12NWRKRX RSKSX RPKUK RPXUX",
	1036: " 27JZNKNX ROKOX RWKOS RQQVX RRQWX RLKQK RTKYK RLXQX RTXYX",
	1037: " 15KYRKMX RRNVX RRKWX RKXPX RTXYX",
	1038: " 30I\\MKMX RNNRX RNKRU RWKRX RWKWX RXKXX RKKNK RWKZK RKXOX RUXZX",
	1039: " 21JZNKNX ROMVX ROKVV RVKVX RLKOK RTKXK RLXPX",
	1040: " 36JZMJLM RXJWM RPPOS RUPTS RMVLY RXVWY RMKWK RMLWL RPQTQ RPRTR RMWWW RMXWX",
	1041: " 32KZQKOLNMMPMSNVOWQXTXVWWVXSXPWMVLTKQK RQKOMNPNSOVQX RTXVVWSWPVMTK",
	1042: " 21J[NKNX ROKOX RVKVX RWKWX RLKYK RLXQX RTXYX",
	1043: " 25JYNKNX ROKOX RLKSKVLWNWOVQSROR RSKULVNVOUQSR RLXQX",
	1044: " 20K[MKRQ RNKSQMX RMKWKXOVK RNWWW RMXWXXTVX",
	1045: " 16KZRKRX RSKSX RNKMOMKXKXOWK RPXUX",
	1046: " 33KZMONLOKPKQLRORX RXOWLVKUKTLSOSX RMONMOLPLQMRO RXOWMVLULTMSO RPXUX",
	1047: " 40KZRKRX RSKSX RQNNOMQMRNTQUTUWTXRXQWOTNQN RQNOONQNROTQU RTUVTWRWQVOTN RPKUK RPXUX",
	1048: " 21KZNKVX ROKWX RWKNX RLKQK RTKYK RLXQX RTXYX",
	1049: " 33J[RKRX RSKSX RLPMONOOSQU RTUVSWOXOYP RMONROTQUTUVTWRXO RPKUK RPXUX",
	1050: " 35KZMVNXQXMRMONMOLQKTKVLWMXOXRTXWXXV ROUNRNOOMQK RTKVMWOWRVU RNWPW RUWWW",
	1051: " 18KYTKKX RSMTX RTKUX RNTTT RIXNX RRXWX",
	1052: " 34JYPKLX RQKMX RNKUKWLWNVPSQ RUKVLVNUPSQ ROQRQTRUSUUTWQXJX RRQTSTUSWQX",
	1053: " 25KXVLWLXKWNVLTKRKPLOMNOMRMUNWPXRXTWUU RRKPMOONRNVPX",
	1054: " 26JYPKLX RQKMX RNKTKVLWNWQVTUVTWQXJX RTKULVNVQUTTVSWQX",
	1055: " 22JYPKLX RQKMX RSORS RNKXKWNWK ROQRQ RJXTXUUSX",
	1056: " 20JXPKLX RQKMX RSORS RNKXKWNWK ROQRQ RJXOX",
	1057: " 33KYVLWLXKWNVLTKRKPLOMNOMRMUNWPXRXTWUVVS RRKPMOONRNVPX RRXTVUS RSSXS",
	1058: " 27J[PKLX RQKMX RXKTX RYKUX RNKSK RVK[K ROQVQ RJXOX RRXWX",
	1059: " 12NWTKPX RUKQX RRKWK RNXSX",
	1060: " 19LXUKRUQWPX RVKSURWPXOXMWLUMTNUMV RSKXK",
	1061: " 27JZPKLX RQKMX RYKOR RRPTX RSPUX RNKSK RVK[K RJXOX RRXWX",
	1062: " 14KXQKMX RRKNX ROKTK RKXUXVUTX",
	1063: " 30I\\OKKX ROMPX RPKQV RYKPX RYKUX RZKVX RMKPK RYK\\K RIXMX RSXXX",
	1064: " 21JZPKLX RPKTX RQKTU RXKTX RNKQK RVKZK RJXNX",
	1065: " 32KYRKPLOMNOMRMUNWPXRXTWUVVTWQWNVLTKRK RRKPMOONRNVPX RRXTVUTVQVMTK",
	1066: " 24JYPKLX RQKMX RNKUKWLXMXOWQTROR RUKWMWOVQTR RJXOX",
	1067: " 46KYRKPLOMNOMRMUNWPXRXTWUVVTWQWNVLTKRK RRKPMOONRNVPX RRXTVUTVQVMTK ROWOVPUQURVRZS[T[UZ RRVSZT[",
	1068: " 35JZPKLX RQKMX RNKUKWLXMXOWQTROR RUKWMWOVQTR RSRTWUXVXWW RSRTSUWVX RJXOX",
	1069: " 28KZWLXLYKXNWLUKRKPLOMOOPPUSVT RONPOURVSVVUWSXPXNWMULXMWNW",
	1070: " 16KZTKPX RUKQX RPKNNOKZKYNYK RNXSX",
	1071: " 20J[PKMUMWOXSXUWVUYK RQKNUNWOX RNKSK RWK[K",
	1072: " 15KYOKPX RPKQV RYKPX RMKRK RVK[K",
	1073: " 24I[NKMX ROKNV RTKMX RTKSX RUKTV RZKSX RLKQK RXK\\K",
	1074: " 21KZPKTX RQKUX RYKLX RNKSK RVK[K RJXOX RRXWX",
	1075: " 20LYPKRQPX RQKSQ RYKSQQX RNKSK RVK[K RNXSX",
	1076: " 16LYXKLX RYKMX RQKONPKYK RLXUXVUTX",
	1101: " 32LZQOPPPQOQOPQOTOVQVWWXXX RTOUQUWWX RURRSPTOUOWPXSXTWUU RRSPUPWQX",
	1102: " 29JYNKNX ROKOX RORPPROTOVPWRWUVWTXRXPWOU RTOUPVRVUUWTX RLKOK",
	1103: " 24LXVQUQURVRVQUPSOQOOPNRNUOWQXSXUWVV RQOPPOROUPWQX",
	1104: " 32L[VKVX RWKWX RVRUPSOQOOPNRNUOWQXSXUWVU RQOPPOROUPWQX RTKWK RVXYX",
	1105: " 26LXOSVSVRUPSOQOOPNRNUOWQXSXUWVV RUSUQSO RQOPPOROUPWQX",
	1106: " 20LWTKULUMVMVLTKRKPMPX RRKQMQX RNOSO RNXSX",
	1107: " 42LYQOOQOSQUSUUSUQSOQO RQOPQPSQU RSUTSTQSO RTPUOVO RPTOUOXPYTYVZ ROWPXTXVYV[T\\P\\N[NYPX",
	1108: " 28J[NKNX ROKOX RORPPROTOVPWRWX RTOUPVRVX RLKOK RLXQX RTXYX",
	1109: " 18NWRKRLSLSKRK RRORX RSOSX RPOSO RPXUX",
	1110: " 23NWSKSLTLTKSK RSOSZR\\ RTOTZR\\P\\O[OZPZP[O[ RQOTO",
	1111: " 27JZNKNX ROKOX RWOOU RRSVX RSSWX RLKOK RTOYO RLXQX RTXYX",
	1112: " 12NWRKRX RSKSX RPKSK RPXUX",
	1113: " 44F_JOJX RKOKX RKRLPNOPORPSRSX RPOQPRRRX RSRTPVOXOZP[R[X RXOYPZRZX RHOKO RHXMX RPXUX RXX]X",
	1114: " 28J[NONX ROOOX RORPPROTOVPWRWX RTOUPVRVX RLOOO RLXQX RTXYX",
	1115: " 28LYQOOPNRNUOWQXTXVWWUWRVPTOQO RQOPPOROUPWQX RTXUWVUVRUPTO",
	1116: " 32JYNON\\ ROOO\\ RORPPROTOVPWRWUVWTXRXPWOU RTOUPVRVUUWTX RLOOO RL\\Q\\",
	1117: " 29KYUOU\\ RVOV\\ RURTPROPONPMRMUNWPXRXTWUU RPOOPNRNUOWPX RS\\X\\",
	1118: " 22KXOOOX RPOPX RPRQPSOUOVPVQUQUPVP RMOPO RMXRX",
	1119: " 26LYTOUPUQVQVPTOQOOPORQSTTVU ROQQRTSVTVWTXQXOWOVPVPWQX",
	1120: " 14LWPKPVRXTXUWUV RQKQVRX RNOTO",
	1121: " 28J[NONUOWQXSXUWVU ROOOUPWQX RVOVX RWOWX RLOOO RTOWO RVXYX",
	1122: " 15KYNORX ROORV RVORX RLOQO RTOXO",
	1123: " 24I[LOOX RMOOU RROOX RROUX RSOUU RXOUX RJOOO RVOZO",
	1124: " 21KYNOUX ROOVX RVONX RLOQO RTOXO RLXPX RSXXX",
	1125: " 23KYNORX ROORV RVORXP[N\\M\\L[LZMZM[L[ RLOQO RTOXO",
	1126: " 16LXUONX RVOOX ROONQNOVO RNXVXVVUX",
	1127: " 32K[QOOPNQMSMUNWPXQXSWUUWRXO RQOOQNSNUOWPX RQOSOUPWWXX RSOTPVWXXYX",
	1128: " 40KXRKPMOOMUK\\ RQLPNNTL\\ RRKTKVLVNUPRQ RTKULUNTPRQ RRQTRUTUVTWRXQXOWNT RRQSRTTTVRX",
	1129: " 19KYLQNOPORPSSSXR\\ RLQNPPPRQSS RWOVRSXQ\\",
	1130: " 39KYSOQOOPNQMSMUNWPXRXTWUVVTVRUPRNQLQKRJTJUKVM RQOOQNSNVPX RRXTVUTUQSO RQLRKTKVM",
	1131: " 27LXVPTOQOOPOQPRRS RQOPPPQRS RRSOTNUNWPXSXUW RRSPTOUOWPX",
	1132: " 28LWRKQLQMSNVNVMSNPOOPNRNTOVPWRXSYS[R\\P\\O[ RSNQOPPOROTPVRX",
	1133: " 26IYJRKPLONOOPOQMX RMONPNQLX ROQPPROTOVPVRS\\ RTOUPURR\\",
	1134: " 35IYJSKQLPNPOQOVPX RMPNQNUOWPXQXSWTVUTVQVNULTKRKQLQNRPURWS RQXSVTTUQUNTK",
	1135: " 13NWROPVPWQXSXUWVU RSOQVQWRX",
	1136: " 26KYOOLX RPOMX RUOVPWPVOTORQOR RORPSRWTXVWWU RORQSSWTX",
	1137: " 15LXLKNKPLWX RNKOLVX RRPMX RRPNX",
	1138: " 26KZOOK\\ RPOL\\ RNUNWOXQXSWTV RVOTVTWUXWXXWYU RWOUVUWVX",
	1139: " 19JYNOMX ROONUMX RVRVOWOVRTUQWNXMX RLOOO",
	1140: " 36MXRKQLQMSNVN RTNQOPPPRRSUS RTNROQPQRRS RSSPTOUOWQXSYTZT[S\\Q\\ RSSQTPUPWQX",
	1141: " 28KXQOOPNQMSMUNWPXRXTWUVVTVRUPSOQO RQOOQNSNVPX RRXTVUTUQSO",
	1142: " 20IZPPMX RPPNX RTPSX RTPTX RKQMOXO RKQMPXP",
	1143: " 29JXSOQOOPNQMSJ\\ RQOOQNSK\\ RSOUPVRVTUVTWRXPXNWMU RSOUQUTTVRX",
	1144: " 28K[YOQOOPNQMSMUNWPXRXTWUVVTVRUPYP RQOOQNSNVPX RRXTVUTUQSO",
	1145: " 14KZSPQX RSPRX RMQOOXO RMQOPXP",
	1146: " 24JXKRLPMOOOPPPROUOWPX RNOOPORNUNWPXQXSWUUVRVOUOVP",
	1147: " 35KZOPNQMSMUNWPXRXUWWUXRXPWOUOTPSRRUO\\ RMUNVPWRWUVWTXR RXQWPUPSR RRUQXP\\",
	1148: " 17KXMONOPPS[T\\ RNOOPR[T\\U\\ RVOTRNYL\\",
	1149: " 28I[TKQ\\ RUKP\\ RJRKPLONOOPOVPWSWUVWT RMONPNTOWPXSXUWWTXRYO",
	1150: " 36JZNPPPPONPMQLSLUMWNXPXQWRUSR RLUNWPWRU RRRRWSXUXWVXTXRWPVOVPWP RRUSWUWWV",
	1151: " 32KZVOTVTWUXWXXWYU RWOUVUWVX RUSUQSOQOOPNQMSMUNWPXRXTV RQOOQNSNVPX",
	1152: " 32JXOKMR RPKNRNVPX RNROPQOSOUPVRVTUVTWRXPXNWMUMR RSOUQUTTVRX RMKPK",
	1153: " 22KXUPUQVQUPSOQOOPNQMSMUNWPXRXTWUV RQOOQNSNVPX",
	1154: " 35KZWKTVTWUXWXXWYU RXKUVUWVX RUSUQSOQOOPNQMSMUNWPXRXTV RQOOQNSNVPX RUKXK",
	1155: " 23KWNURTTSURUPSOQOOPNQMSMUNWPXRXTWUV RQOOQNSNVPX",
	1156: " 23MXWKXLXKVKTLSNPYO[N\\ RVKULTNQYP[N\\L\\L[M\\ RPOVO",
	1157: " 34KYVOTVSYR[ RWOUVTYR[P\\M\\L[M[N\\ RUSUQSOQOOPNQMSMUNWPXRXTV RQOOQNSNVPX",
	1158: " 29KZPKLX RQKMX ROQPPROTOVPVRUUUWVX RTOUPURTUTWUXWXXWYU RNKQK",
	1159: " 26MWSKSLTLTKSK RNROPPOROSPSRRURWSX RQORPRRQUQWRXTXUWVU",
	1160: " 26MWTKTLULUKTK RORPPQOSOTPTRRYQ[O\\M\\M[N\\ RROSPSRQYP[O\\",
	1161: " 32KXPKLX RQKMX RVPUQVQVPUOTORQPROR RORPSQWRXTXUWVU RORQSRWSX RNKQK",
	1162: " 16NVSKPVPWQXSXTWUU RTKQVQWRX RQKTK",
	1163: " 46F^GRHPIOKOLPLQJX RJOKPKQIX RLQMPOOQOSPSQQX RQORPRQPX RSQTPVOXOZPZRYUYWZX RXOYPYRXUXWYX[X\\W]U",
	1164: " 33J[KRLPMOOOPPPQNX RNOOPOQMX RPQQPSOUOWPWRVUVWWX RUOVPVRUUUWVXXXYWZU",
	1165: " 28KXQOOPNQMSMUNWPXRXTWUVVTVRUPSOQO RQOOQNSNVPX RRXTVUTUQSO",
	1166: " 35JYKRLPMOOOPPPQM\\ RNOOPOQL\\ RPQROTOVPWRWTVVUWSXQXOVOT RTOVQVTUVSX RJ\\O\\",
	1167: " 28KYVOR\\ RWOS\\ RUSUQSOQOOPNQMSMUNWPXRXTV RQOOQNSNVPX RP\\U\\",
	1168: " 22LXMRNPOOQORPRQPX RPOQPQQOX RRQSPUOVOWPWQVQWP",
	1169: " 24LYVPVQWQVPTOQOOPORQSTTVU ROQQRTSVTVWTXQXOWNVOVOW",
	1170: " 16NWSKPVPWQXSXTWUU RTKQVQWRX RPOUO",
	1171: " 33IZJRKPLONOOPORNUNWOX RMONPNRMUMWOXQXSWTV RVOTVTWUXWXXWYU RWOUVUWVX",
	1172: " 24JXKRLPMOOOPPPROUOWPX RNOOPORNUNWPXQXSWUUVRVOUOVP",
	1173: " 37H\\IRJPKOMONPNRMUMWNX RLOMPMRLULWNXOXQWRV RTORVRWTX RUOSVSWTXUXWWYUZRZOYOZP",
	1174: " 38JZMRNPPOROSPSR RQORPRRQUPWNXMXLWLVMVLW RXPWQXQXPWOVOTPSRRURWSX RQUQWRXTXVWWU",
	1175: " 35IYJRKPLONOOPORNUNWOX RMONPNRMUMWOXQXSWTV RVOTVSYR[ RWOUVTYR[P\\M\\L[M[N\\",
	1176: " 27KYWOWPVQNVMWMX RNQOOROUQ ROPRPUQVQ RNVOVRWUW ROVRXUXVV",
	1177: " 39H[RKSLSMTMTLRKOKMLLNLX ROKNLMNMX RXKYLYMZMZLXKVKTMTX RVKUMUX RJOWO RJXOX RRXWX",
	1178: " 29J[UKVLWLWKQKOLNNNX RQKPLONOX RVOVX RWOWX RLOWO RLXQX RTXYX",
	1179: " 27J[WKQKOLNNNX RQKPLONOX RUKVLVX RWKWX RLOVO RLXQX RTXYX",
	1180: " 48F_PKQLQMRMRLPKMKKLJNJX RMKLLKNKX RYKZL[L[KUKSLRNRX RUKTLSNSX RZOZX R[O[X RHO[O RHXMX RPXUX RXX]X",
	1181: " 46F_PKQLQMRMRLPKMKKLJNJX RMKLLKNKX R[KUKSLRNRX RUKTLSNSX RYKZLZX R[K[X RHOZO RHXMX RPXUX RXX]X",
	1182: " 12NWRORX RSOSX RPOSO RPXUX",
	1184: " 21LXVPTOROPPOQNSNUOWQXSXUW RROPQOSOVQX ROSSS",
	1185: " 35LYSKQLPMOONRNUOWPXRXTWUVVTWQWNVLUKSK RSKQMPOOSOVPX RRXTVUTVPVMUK ROQVQ",
	1186: " 34KZTKQ\\ RUKP\\ RQONPMRMUNWQXTXWWXUXRWPTOQO RQOOPNRNUOWQX RTXVWWUWRVPTO",
	1187: " 22LXUPVRVQUPSOQOOPNRNTOVRX RQOOQOTPVRXSYS[R\\P\\",
	1191: " 45I[VKWLXLVKSKQLPMOOLYK[J\\ RSKQMPOMYL[J\\H\\H[I\\ RZK[L[KYKWLVNSYR[Q\\ RYKXLWNTYS[Q\\O\\O[P\\ RLOYO",
	1192: " 38IZVKWLXLXKSKQLPMOOLYK[J\\ RSKQMPOMYL[J\\H\\H[I\\ RVOTVTWUXWXXWYU RWOUVUWVX RLOWO",
	1193: " 38IZVKWL RXKSKQLPMOOLYK[J\\ RSKQMPOMYL[J\\H\\H[I\\ RWKTVTWUXWXXWYU RXKUVUWVX RLOVO",
	1194: " 63F^SKTLTM RULSKPKNLMMLOIYH[G\\ RPKNMMOJYI[G\\E\\E[F\\ RZK[L\\L\\KWKUL RTMSOPYO[N\\ RWKUMTOQYP[N\\L\\L[M\\ RZOXVXWYX[X\\W]U R[OYVYWZX RIO[O",
	1195: " 63F^SKTLTM RULSKPKNLMMLOIYH[G\\ RPKNMMOJYI[G\\E\\E[F\\ RZK[L R\\KWKUL RTMSOPYO[N\\ RWKUMTOQYP[N\\L\\L[M\\ R[KXVXWYX[X\\W]U R\\KYVYWZX RIOZO",
	1196: " 20MWNROPPOROSPSRRURWSX RQORPRRQUQWRXTXUWVU",
	1200: " 28LYQKOLNONTOWQXTXVWWTWOVLTKQK RQKPLOOOTPWQX RTXUWVTVOULTK",
	1201: " 10LYPNSKSX RRLRX ROXVX",
	1202: " 35LYOMONNNNMOLQKTKVLWNVPTQQROSNUNX RTKULVNUPTQ RNWOVPVSWVWWV RPVSXVXWVWU",
	1203: " 39LYOMONNNNMOLQKTKVLWNVPTQ RTKULVNUPTQ RRQTQVRWTWUVWTXQXOWNVNUOUOV RTQURVTVUUWTX",
	1204: " 13LYSMSX RTKTX RTKMTXT RQXVX",
	1205: " 33LYOKNQ ROKVK ROLSLVK RNQOPQOTOVPWRWUVWTXQXOWNVNUOUOV RTOUPVRVUUWTX",
	1206: " 36LYVMVNWNWMVLTKRKPLOMNPNUOWQXTXVWWUWSVQTPQPNR RRKPMOPOUPWQX RTXUWVUVSUQTP",
	1207: " 22LYNKNO RVMRTPX RWKTQQX RNMPKRKUM RNMPLRLUMVM",
	1208: " 51LYQKOLNNOPQQTQVPWNVLTKQK RQKPLONPPQQ RTQUPVNULTK RQQORNTNUOWQXTXVWWUWTVRTQ RQQPROTOUPWQX RTXUWVUVTURTQ",
	1209: " 36LYOVOUNUNVOWQXSXUWVVWSWNVLTKQKOLNNNPORQSTSWQ RSXUVVSVNULTK RQKPLONOPPRQS",
	1210: "  6NVRVQWRXSWRV",
	1211: "  8NVSWRXQWRVSWSYQ[",
	1212: " 12NVROQPRQSPRO RRVQWRXSWRV",
	1213: " 14NVROQPRQSPRO RSWRXQWRVSWSYQ[",
	1214: " 15NVRKQLRSSLRK RRLRO RRVQWRXSWRV",
	1215: " 29LYNNONOONONNOLQKTKVLWNWOVQSRRSRTST RTKVMVPUQSR RRWRXSXSWRW",
	1216: "  6OVRKRP RSKRP",
	1217: " 12LXOKOP RPKOP RUKUP RVKUP",
	1218: " 10MWQKPLPNQOSOTNTLSKQK",
	1219: "  9MWRJRP ROKUO RUKOO",
	1220: "  3KZXHM\\",
	1221: " 16MWUHSJQMPPPTQWSZU\\ RSJRLQPQTRXSZ",
	1222: " 16MWOHQJSMTPTTSWQZO\\ RQJRLSPSTRXQZ",
	1223: " 12MWPHP\\ RQHQ\\ RPHUH RP\\U\\",
	1224: " 12MWSHS\\ RTHT\\ ROHTH RO\\T\\",
	1225: " 38LWSHQIPJPLRNSP RQIPL RSNRQ RPJQLSNSPRQPRRSSTSVQXPZ RRSSV RPXQ[ RSTRVPXPZQ[S\\",
	1226: " 38MXQHSITJTLRNQP RSITL RQNRQ RTJSLQNQPRQTRRSQTQVSXTZ RRSQV RTXS[ RQTRVTXTZS[Q\\",
	1227: "  4MWTHPRT\\",
	1228: "  4MWPHTRP\\",
	1229: "  3OURHR\\",
	1230: "  6MWPHP\\ RTHT\\",
	1231: "  3I[LRXR",
	1232: "  6I[RLRX RLRXR",
	1233: "  9JZRMRX RMRWR RMXWX",
	1234: "  9JZRMRX RMMWM RMRWR",
	1235: "  6JZMMWW RWMMW",
	1236: "  6NVRQQRRSSRRQ",
	1237: " 15I[RLQMRNSMRL RLRXR RRVQWRXSWRV",
	1238: "  6I[LPXP RLTXT",
	1239: "  9I[WLMX RLPXP RLTXT",
	1240: "  9I[LNXN RLRXR RLVXV",
	1241: "  4JZWLMRWX",
	1242: "  4JZMLWRMX",
	1243: " 10JZWKMOWS RMTWT RMXWX",
	1244: " 10JZMKWOMS RMTWT RMXWX",
	1245: " 21H[YUWUUTTSRPQOONNNLOKQKRLTNUOUQTRSTPUOWNYN",
	1246: " 16JZLTLRMPOPUSWSXR RLRMQOQUTWTXRXP",
	1247: "  8JZMSRPWS RMSRQWS",
	1248: "  7NVSKPO RSKTLPO",
	1249: "  7NVQKTO RQKPLTO",
	1250: " 14LXNKOMQNSNUMVK RNKONQOSOUNVK",
	1251: "  8NVSLRMQLRKSLSNQP",
	1252: "  8NVSKQMQORPSORNQO",
	1253: "  8NVQLRMSLRKQLQNSP",
	1254: "  8NVQKSMSORPQORNSO",
	1256: " 11JZWMQMONNOMQMSNUOVQWWW",
	1257: " 11JZMMMSNUOVQWSWUVVUWSWM",
	1258: " 11JZMMSMUNVOWQWSVUUVSWMW",
	1259: " 11JZMWMQNOONQMSMUNVOWQWW",
	1260: " 14JZWMQMONNOMQMSNUOVQWWW RMRUR",
	1261: " 13I[TOUPXRUTTU RUPWRUT RLRWR",
	1262: " 13MWRMRX ROPPORLTOUP RPORMTO",
	1263: " 13I[POOPLROTPU ROPMROT RMRXR",
	1264: " 13MWRLRW ROTPURXTUUT RPURWTU",
	1265: " 37KYVSUPSOQOOPNQMSMUNWPXRXTWUVVTWQWNVLTKQKPLQLRK RQOOQNSNVPX RRXTVUTVQVNULTK",
	1266: " 15JZLKRX RMKRV RXKRX RLKXK RNLWL",
	1267: " 10G[IOLORW RKORX R[FRX",
	1268: " 26I[XIXJYJYIXHVHTJSLROQUPYO[ RUITKSORUQXPZN\\L\\K[KZLZL[",
	1269: " 40I[XIXJYJYIXHVHTJSLROQUPYO[ RUITKSORUQXPZN\\L\\K[KZLZL[ RQNOONQNSOUQVSVUUVSVQUOSNQN",
	1270: " 26H\\ZRYTWUVUTTSSQPPONNMNKOJQJRKTMUNUPTQSSPTOVNWNYOZQZR",
	1271: " 26JZXKLX ROKPLPNOOMOLNLLMKOKSLVLXK RUTTUTWUXWXXWXUWTUT",
	1272: " 41J[YPXPXQYQYPXOWOVPUTTVSWQXOXMWLVLTMSORRPSNSLRKPKOLONPQUWWXXXYW ROXMVMTOR RONPPVWWX",
	1273: " 29J[UPSOQOPQPRQTSTUS RUOUSVTXTYRYQXNVLSKRKOLMNLQLRMUOWRXSXVW",
	1274: " 34KZQHQ\\ RTHT\\ RWLVLVMWMWLUKPKNLNNOPVSWT RNNOOVRWTWVVWTXQXOWNVNUOUOVNV",
	1275: " 12KYRKN\\ RVKR\\ RNQWQ RMVVV",
	1276: " 40LXTLSLSMTMTLSKQKPLPNQPTRUS RPNQOTQUSUUSW RQPOROTPVSXTY ROTPUSWTYT[S\\Q\\P[PZQZQ[P[",
	1277: " 29LXRKQLRMSLRK RRMRQ RRQQSRVSSRQ RRVR\\ RPOONNOOPPOTOUNVOUPTO",
	1278: " 42LXRMSLRKQLRMRQQRSURV RRQSRQURVRZQ[R\\S[RZ RPOONNOOPPOTOUNVOUPTO RPXOWNXOYPXTXUWVXUYTX",
	1279: " 12LYVKVX RNKVK RQQVQ RNXVX",
	1281: " 24H\\QKNLLNKQKSLVNXQYSYVXXVYSYQXNVLSKQK RRQQRRSSRRQ",
	1282: " 33LYQKPLPMQN RTKULUMTN RRNPOOQORPTRUSUUTVRVQUOSNRN RRURY RSUSY ROWVW",
	1283: " 23LYRKPLONOOPQRRSRUQVOVNULSKRK RRRRX RSRSX ROUVU",
	1284: " 24H\\QKNLLNKQKSLVNXQYSYVXXVYSYQXNVLSKQK RRKRY RKRYR",
	1285: " 25JYRRPQOQMRLTLUMWOXPXRWSUSTRR RWMRR RRMWMWR RRMVNWR",
	1286: " 25JZLLMKOKQLRNRPQRPSNT ROKPLQNQQPS RVKUX RWKTX RNTXT",
	1287: " 27JYNKNU ROKNR RNROPQOSOUPVQVTTVTXUYVYWX RSOUQUTTV RLKOK",
	1288: " 27LYONRKRQ RVNSKSQ RRQPROTOUPWRXSXUWVUVTURSQ RRTRUSUSTRT",
	1289: " 27JZRKRY RMKMPNRPSTSVRWPWK RLMMKNM RQMRKSM RVMWKXM ROVUV",
	1290: " 27JYNKNX ROKOX RLKSKVLWNWOVQSROR RSKULVNVOUQSR RLXVXVUUX",
	1291: " 20LYWKTKQLONNQNSOVQXTYWY RWKTLRNQQQSRVTXWY",
	1292: " 23JZRRPQOQMRLTLUMWOXPXRWSUSTRR RSLQQ RWMRR RXQSS",
	1293: " 12KYPMTW RTMPW RMPWT RWPMT",
	1294: " 34J[OUMULVLXMYOYPXPVNTMRMONMOLQKTKVLWMXOXRWTUVUXVYXYYXYVXUVU RNMPLULWM",
	1295: " 34J[OOMOLNLLMKOKPLPNNPMRMUNWOXQYTYVXWWXUXRWPUNULVKXKYLYNXOVO RNWPXUXWW",
	1401: " 21F^KHK\\ RLHL\\ RXHX\\ RYHY\\ RHH\\H RH\\O\\ RU\\\\\\",
	1402: " 20H]KHRQJ\\ RJHQQ RJHYHZMXH RK[X[ RJ\\Y\\ZWX\\",
	1403: " 20KYVBTDRGPKOPOTPYR]T`Vb RTDRHQKPPPTQYR\\T`",
	1404: " 20KYNBPDRGTKUPUTTYR]P`Nb RPDRHSKTPTTSYR\\P`",
	1405: " 12KYOBOb RPBPb ROBVB RObVb",
	1406: " 12KYTBTb RUBUb RNBUB RNbUb",
	1407: " 40KYTBRCQDPFPHQJRKSMSOQQ RRCQEQGRISJTLTNSPORSTTVTXSZR[Q]Q_Ra RQSSUSWRYQZP\\P^Q`RaTb",
	1408: " 40KYPBRCSDTFTHSJRKQMQOSQ RRCSESGRIQJPLPNQPURQTPVPXQZR[S]S_Ra RSSQUQWRYSZT\\T^S`RaPb",
	1409: " 24KYU@RCPFOIOLPOSVTYT\\S_Ra RRCQEPHPKQNTUUXU[T^RaOd",
	1410: " 24KYO@RCTFUIULTOQVPYP\\Q_Ra RRCSETHTKSNPUOXO[P^RaUd",
	1411: " 13AXCRGRR` RGSRa RFSRb RX:Rb",
	1412: " 32F^[CZD[E\\D\\C[BYBWCUETGSJRNPZO^N` RVDUFTJRVQZP]O_MaKbIbHaH`I_J`Ia",
	2001: " 18H\\RFK[ RRFY[ RRIX[ RMUVU RI[O[ RU[[[",
	2002: " 45G]LFL[ RMFM[ RIFUFXGYHZJZLYNXOUP RUFWGXHYJYLXNWOUP RMPUPXQYRZTZWYYXZU[I[ RUPWQXRYTYWXYWZU[",
	2003: " 32G\\XIYLYFXIVGSFQFNGLIKKJNJSKVLXNZQ[S[VZXXYV RQFOGMILKKNKSLVMXOZQ[",
	2004: " 30G]LFL[ RMFM[ RIFSFVGXIYKZNZSYVXXVZS[I[ RSFUGWIXKYNYSXVWXUZS[",
	2005: " 22G\\LFL[ RMFM[ RSLST RIFYFYLXF RMPSP RI[Y[YUX[",
	2006: " 20G[LFL[ RMFM[ RSLST RIFYFYLXF RMPSP RI[P[",
	2007: " 40G^XIYLYFXIVGSFQFNGLIKKJNJSKVLXNZQ[S[VZXX RQFOGMILKKNKSLVMXOZQ[ RXSX[ RYSY[ RUS\\S",
	2008: " 27F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\\F RLPXP RH[O[ RU[\\[",
	2009: " 12MXRFR[ RSFS[ ROFVF RO[V[",
	2010: " 20KZUFUWTZR[P[NZMXMVNUOVNW RTFTWSZR[ RQFXF",
	2011: " 27F\\KFK[ RLFL[ RYFLS RQOY[ RPOX[ RHFOF RUF[F RH[O[ RU[[[",
	2012: " 14I[NFN[ ROFO[ RKFRF RK[Z[ZUY[",
	2013: " 30F_KFK[ RLFRX RKFR[ RYFR[ RYFY[ RZFZ[ RHFLF RYF]F RH[N[ RV[][",
	2014: " 21G^LFL[ RMFYY RMHY[ RYFY[ RIFMF RVF\\F RI[O[",
	2015: " 44G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF",
	2016: " 29G]LFL[ RMFM[ RIFUFXGYHZJZMYOXPUQMQ RUFWGXHYJYMXOWPUQ RI[P[",
	2017: " 64G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF RNYNXOVQURUTVUXV_W`Y`Z^Z] RUXV\\W^X_Y_Z^",
	2018: " 45G]LFL[ RMFM[ RIFUFXGYHZJZLYNXOUPMP RUFWGXHYJYLXNWOUP RI[P[ RRPTQURXYYZZZ[Y RTQUSWZX[Z[[Y[X",
	2019: " 34H\\XIYFYLXIVGSFPFMGKIKKLMMNOOUQWRYT RKKMMONUPWQXRYTYXWZT[Q[NZLXKUK[LX",
	2020: " 16I\\RFR[ RSFS[ RLFKLKFZFZLYF RO[V[",
	2021: " 23F^KFKULXNZQ[S[VZXXYUYF RLFLUMXOZQ[ RHFOF RVF\\F",
	2022: " 15H\\KFR[ RLFRX RYFR[ RIFOF RUF[F",
	2023: " 24F^JFN[ RKFNV RRFN[ RRFV[ RSFVV RZFV[ RGFNF RWF]F",
	2024: " 21H\\KFX[ RLFY[ RYFK[ RIFOF RUF[F RI[O[ RU[[[",
	2025: " 20H]KFRQR[ RLFSQS[ RZFSQ RIFOF RVF\\F RO[V[",
	2026: " 16H\\XFK[ RYFL[ RLFKLKFYF RK[Y[YUX[",
	2027: " 18H\\RFK[ RRFY[ RRIX[ RMUVU RI[O[ RU[[[",
	2028: " 45G]LFL[ RMFM[ RIFUFXGYHZJZLYNXOUP RUFWGXHYJYLXNWOUP RMPUPXQYRZTZWYYXZU[I[ RUPWQXRYTYWXYWZU[",
	2029: " 14I[NFN[ ROFO[ RKFZFZLYF RK[R[",
	2030: " 15H\\RFJ[ RRFZ[ RRIY[ RKZYZ RJ[Z[",
	2031: " 22G\\LFL[ RMFM[ RSLST RIFYFYLXF RMPSP RI[Y[YUX[",
	2032: " 16H\\XFK[ RYFL[ RLFKLKFYF RK[Y[YUX[",
	2033: " 27F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\\F RLPXP RH[O[ RU[\\[",
	2034: " 56G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF ROMOT RUMUT ROPUP ROQUQ",
	2035: " 12MXRFR[ RSFS[ ROFVF RO[V[",
	2036: " 27F\\KFK[ RLFL[ RYFLS RQOY[ RPOX[ RHFOF RUF[F RH[O[ RU[[[",
	2037: " 15H\\RFK[ RRFY[ RRIX[ RI[O[ RU[[[",
	2038: " 30F_KFK[ RLFRX RKFR[ RYFR[ RYFY[ RZFZ[ RHFLF RYF]F RH[N[ RV[][",
	2039: " 21G^LFL[ RMFYY RMHY[ RYFY[ RIFMF RVF\\F RI[O[",
	2040: " 36G]KEJJ RZEYJ RONNS RVNUS RKWJ\\ RZWY\\ RKGYG RKHYH ROPUP ROQUQ RKYYY RKZYZ",
	2041: " 44G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF",
	2042: " 21F^KFK[ RLFL[ RXFX[ RYFY[ RHF\\F RH[O[ RU[\\[",
	2043: " 29G]LFL[ RMFM[ RIFUFXGYHZJZMYOXPUQMQ RUFWGXHYJYMXOWPUQ RI[P[",
	2044: " 20H]KFRPJ[ RJFQP RJFYFZLXF RKZXZ RJ[Y[ZUX[",
	2045: " 16I\\RFR[ RSFS[ RLFKLKFZFZLYF RO[V[",
	2046: " 33I\\KKKILGMFOFPGQIRMR[ RKIMGOGQI RZKZIYGXFVFUGTISMS[ RZIXGVGTI RO[V[",
	2047: " 48H]RFR[ RSFS[ RPKMLLMKOKRLTMUPVUVXUYTZRZOYMXLUKPK RPKNLMMLOLRMTNUPV RUVWUXTYRYOXMWLUK ROFVF RO[V[",
	2048: " 21H\\KFX[ RLFY[ RYFK[ RIFOF RUF[F RI[O[ RU[[[",
	2049: " 41G^RFR[ RSFS[ RIMJLLMMQNSOTQU RJLKMLQMSNTQUTUWTXSYQZM[L RTUVTWSXQYM[L\\M ROFVF RO[V[",
	2050: " 43G]JXK[O[MWKSJPJLKIMGPFTFWGYIZLZPYSWWU[Y[ZX RMWLTKPKLLINGPF RTFVGXIYLYPXTWW RKZNZ RVZYZ",
	2051: " 18H\\UFH[ RUFV[ RTHU[ RLUUU RF[L[ RR[X[",
	2052: " 41F^OFI[ RPFJ[ RLFWFZG[I[KZNYOVP RWFYGZIZKYNXOVP RMPVPXQYSYUXXVZR[F[ RVPWQXSXUWXUZR[",
	2053: " 34H]ZH[H\\F[L[JZHYGWFTFQGOIMLLOKSKVLYMZP[S[UZWXXV RTFRGPINLMOLSLVMYNZP[",
	2054: " 30F]OFI[ RPFJ[ RLFUFXGYHZKZOYSWWUYSZO[F[ RUFWGXHYKYOXSVWTYRZO[",
	2055: " 22F]OFI[ RPFJ[ RTLRT RLF[FZLZF RMPSP RF[U[WVT[",
	2056: " 20F\\OFI[ RPFJ[ RTLRT RLF[FZLZF RMPSP RF[M[",
	2057: " 42H^ZH[H\\F[L[JZHYGWFTFQGOIMLLOKSKVLYMZP[R[UZWXYT RTFRGPINLMOLSLVMYNZP[ RR[TZVXXT RUT\\T",
	2058: " 27E_NFH[ ROFI[ R[FU[ R\\FV[ RKFRF RXF_F RLPXP RE[L[ RR[Y[",
	2059: " 12LYUFO[ RVFP[ RRFYF RL[S[",
	2060: " 21I[XFSWRYQZO[M[KZJXJVKULVKW RWFRWQYO[ RTF[F",
	2061: " 27F]OFI[ RPFJ[ R]FLS RSOW[ RROV[ RLFSF RYF_F RF[M[ RS[Y[",
	2062: " 14H\\QFK[ RRFL[ RNFUF RH[W[YUV[",
	2063: " 30E`NFH[ RNFO[ ROFPY R\\FO[ R\\FV[ R]FW[ RKFOF R\\F`F RE[K[ RS[Z[",
	2064: " 21F_OFI[ ROFVX ROIV[ R\\FV[ RLFOF RYF_F RF[L[",
	2065: " 42G]SFPGNILLKOJSJVKYLZN[Q[TZVXXUYRZNZKYHXGVFSF RSFQGOIMLLOKSKVLYN[ RQ[SZUXWUXRYNYKXHVF",
	2066: " 27F]OFI[ RPFJ[ RLFXF[G\\I\\K[NYPUQMQ RXFZG[I[KZNXPUQ RF[M[",
	2067: " 61G]SFPGNILLKOJSJVKYLZN[Q[TZVXXUYRZNZKYHXGVFSF RSFQGOIMLLOKSKVLYN[ RQ[SZUXWUXRYNYKXHVF RLYLXMVOUPURVSXS_T`V`W^W] RSXT^U_V_W^",
	2068: " 42F^OFI[ RPFJ[ RLFWFZG[I[KZNYOVPMP RWFYGZIZKYNXOVP RRPTQURVZW[Y[ZYZX RURWYXZYZZY RF[M[",
	2069: " 35G^ZH[H\\F[L[JZHYGVFRFOGMIMKNMONVRXT RMKOMVQWRXTXWWYVZS[O[LZKYJWJUI[JYKY",
	2070: " 16H]UFO[ RVFP[ ROFLLNF]F\\L\\F RL[S[",
	2071: " 25F_NFKQJUJXKZN[R[UZWXXU\\F ROFLQKUKXLZN[ RKFRF RYF_F",
	2072: " 15H\\NFO[ ROFPY R\\FO[ RLFRF RXF^F",
	2073: " 24E_MFK[ RNFLY RUFK[ RUFS[ RVFTY R]FS[ RJFQF RZF`F",
	2074: " 21G]NFU[ ROFV[ R\\FH[ RLFRF RXF^F RF[L[ RR[X[",
	2075: " 20H]NFRPO[ ROFSPP[ R]FSP RLFRF RYF_F RL[S[",
	2076: " 16G][FH[ R\\FI[ ROFLLNF\\F RH[V[XUU[",
	2077: " 46H\\KILKXWYYY[ RLLXX RKIKKLMXYY[ RPPLTKVKXLZK[ RKVMZ RLTLVMXMZK[ RSSXN RVIVLWNYNYLWKVI RVIWLYN",
	2101: " 39I]NONPMPMONNPMTMVNWOXQXXYZZ[ RWOWXXZZ[[[ RWQVRPSMTLVLXMZP[S[UZWX RPSNTMVMXNZP[",
	2102: " 33G\\LFL[ RMFM[ RMPONQMSMVNXPYSYUXXVZS[Q[OZMX RSMUNWPXSXUWXUZS[ RIFMF",
	2103: " 28H[WPVQWRXQXPVNTMQMNNLPKSKULXNZQ[S[VZXX RQMONMPLSLUMXOZQ[",
	2104: " 36H]WFW[ RXFX[ RWPUNSMQMNNLPKSKULXNZQ[S[UZWX RQMONMPLSLUMXOZQ[ RTFXF RW[[[",
	2105: " 31H[LSXSXQWOVNTMQMNNLPKSKULXNZQ[S[VZXX RWSWPVN RQMONMPLSLUMXOZQ[",
	2106: " 22KXUGTHUIVHVGUFSFQGPIP[ RSFRGQIQ[ RMMUM RM[T[",
	2107: " 60I\\QMONNOMQMSNUOVQWSWUVVUWSWQVOUNSMQM RONNPNTOV RUVVTVPUN RVOWNYMYNWN RNUMVLXLYM[P\\U\\X]Y^ RLYMZP[U[X\\Y^Y_XaUbObLaK_K^L\\O[",
	2108: " 28G]LFL[ RMFM[ RMPONRMTMWNXPX[ RTMVNWPW[ RIFMF RI[P[ RT[[[",
	2109: " 18MXRFQGRHSGRF RRMR[ RSMS[ ROMSM RO[V[",
	2110: " 25MXSFRGSHTGSF RTMT_SaQbObNaN`O_P`Oa RSMS_RaQb RPMTM",
	2111: " 27G\\LFL[ RMFM[ RWMMW RRSX[ RQSW[ RIFMF RTMZM RI[P[ RT[Z[",
	2112: " 12MXRFR[ RSFS[ ROFSF RO[V[",
	2113: " 44BcGMG[ RHMH[ RHPJNMMOMRNSPS[ ROMQNRPR[ RSPUNXMZM]N^P^[ RZM\\N]P][ RDMHM RD[K[ RO[V[ RZ[a[",
	2114: " 28G]LML[ RMMM[ RMPONRMTMWNXPX[ RTMVNWPW[ RIMMM RI[P[ RT[[[",
	2115: " 36H\\QMNNLPKSKULXNZQ[S[VZXXYUYSXPVNSMQM RQMONMPLSLUMXOZQ[ RS[UZWXXUXSWPUNSM",
	2116: " 36G\\LMLb RMMMb RMPONQMSMVNXPYSYUXXVZS[Q[OZMX RSMUNWPXSXUWXUZS[ RIMMM RIbPb",
	2117: " 33H\\WMWb RXMXb RWPUNSMQMNNLPKSKULXNZQ[S[UZWX RQMONMPLSLUMXOZQ[ RTb[b",
	2118: " 23IZNMN[ ROMO[ ROSPPRNTMWMXNXOWPVOWN RKMOM RK[R[",
	2119: " 32J[WOXMXQWOVNTMPMNNMOMQNRPSUUWVXW RMPNQPRUTWUXVXYWZU[Q[OZNYMWM[NY",
	2120: " 16KZPFPWQZS[U[WZXX RQFQWRZS[ RMMUM",
	2121: " 28G]LMLXMZP[R[UZWX RMMMXNZP[ RWMW[ RXMX[ RIMMM RTMXM RW[[[",
	2122: " 15I[LMR[ RMMRY RXMR[ RJMPM RTMZM",
	2123: " 24F^JMN[ RKMNX RRMN[ RRMV[ RSMVX RZMV[ RGMNM RWM]M",
	2124: " 21H\\LMW[ RMMX[ RXML[ RJMPM RTMZM RJ[P[ RT[Z[",
	2125: " 22H[LMR[ RMMRY RXMR[P_NaLbKbJaK`La RJMPM RTMZM",
	2126: " 16I[WML[ RXMM[ RMMLQLMXM RL[X[XWW[",
	2127: " 40G^QMNNLPKRJUJXKZN[P[RZUWWTYPZM RQMONMPLRKUKXLZN[ RQMSMUNVPXXYZZ[ RSMTNUPWXXZZ[[[",
	2128: " 57G\\TFQGOIMMLPKTJZIb RTFRGPINMMPLTKZJb RTFVFXGYHYKXMWNTOPO RVFXHXKWMVNTO RPOTPVRWTWWVYUZR[P[NZMYLV RPOSPURVTVWUYTZR[",
	2129: " 28H\\IPKNMMOMQNROSRSVRZOb RJOLNPNRO RZMYPXRSYP^Nb RYMXPWRSY",
	2130: " 44I\\VNTMRMONMQLTLWMYNZP[R[UZWWXTXQWOSJRHRFSEUEWFYH RRMPNNQMTMXNZ RR[TZVWWTWPVNTKSISGTFVFYH",
	2131: " 32I[XPVNTMPMNNNPPRSS RPMONOPQRSS RSSNTLVLXMZP[S[UZWX RSSOTMVMXNZP[",
	2132: " 31I[TFRGQHQIRJUKZKZJWKSMPOMRLULWMYP[S]T_TaSbQbPa RULQONRMUMWNYP[",
	2133: " 32G]HQIOKMNMONOPNTL[ RMMNNNPMTK[ RNTPPRNTMVMXNYOYRXWUb RVMXOXRWWTb",
	2134: " 44F]GQHOJMMMNNNPMUMXNZO[ RLMMNMPLULXMZO[Q[SZUXWUXRYMYIXGVFTFRHRJSMUPWRZT RSZUWVUWRXMXIWGVF",
	2135: " 15LXRMPTOXOZP[S[UYVW RSMQTPXPZQ[",
	2136: " 29H\\NMJ[ ROMK[ RXMYNZNYMWMUNQROSMS ROSQTSZT[ ROSPTRZS[U[WZYW",
	2137: " 23H\\KFMFOGPHQJWXXZY[ RMFOHPJVXWZY[Z[ RRMJ[ RRMK[",
	2138: " 28F]MMGb RNMHb RMPLVLYN[P[RZTXVU RXMUXUZV[Y[[Y\\W RYMVXVZW[",
	2139: " 24H\\NML[ ROMNSMXL[ RYMXQVU RZMYPXRVUTWQYOZL[ RKMOM",
	2140: " 45IZTFRGQHQIRJUKXK RUKQLOMNONQPSSTVT RUKRLPMOOOQQSST RSTOUMVLXLZN\\S^T_TaRbPb RSTPUNVMXMZO\\S^",
	2141: " 32I[RMONMQLTLWMYNZP[R[UZWWXTXQWOVNTMRM RRMPNNQMTMXNZ RR[TZVWWTWPVN",
	2142: " 22G]PNL[ RPNM[ RVNV[ RVNW[ RIPKNNM[M RIPKONN[N",
	2143: " 31H[LVMYNZP[R[UZWWXTXQWOVNTMRMONMQLTHb RR[TZVWWTWPVN RRMPNNQMTIb",
	2144: " 35H][MQMNNLQKTKWLYMZO[Q[TZVWWTWQVOUNSM RQMONMQLTLXMZ RQ[SZUWVTVPUN RUN[N",
	2145: " 16H\\SNP[ RSNQ[ RJPLNOMZM RJPLOONZN",
	2146: " 31H\\IQJOLMOMPNPPNVNYP[ RNMONOPMVMYNZP[Q[TZVXXUYRYOXMWNXOYR RXUYO",
	2147: " 37G]ONMOKQJTJWKYLZN[Q[TZWXYUZRZOXMVMTORSPXMb RJWLYNZQZTYWWYU RZOXNVNTPRSPYNb",
	2148: " 23I[KMMMONPPU_VaWb RMMNNOPT_UaWbYb RZMYOWRM]K`Jb",
	2149: " 34F]UFOb RVFNb RGQHOJMMMNNNPMUMXOZRZTYWVYS RLMMNMPLULXMZO[R[TZVXXUYS[M",
	2150: " 44F]JQLOONNMLNJQITIWJZK[M[OZQWRT RIWJYKZMZOYQW RQTQWRZS[U[WZYWZTZQYNXMWNYOZQ RQWRYSZUZWYYW",
	2151: " 39H]XMVTUXUZV[Y[[Y\\W RYMWTVXVZW[ RVTVQUNSMQMNNLQKTKWLYMZO[Q[SZUWVT RQMONMQLTLXMZ",
	2152: " 36H[PFLSLVMYNZ RQFMS RMSNPPNRMTMVNWOXQXTWWUZR[P[NZMWMS RVNWPWTVWTZR[ RMFQF",
	2153: " 25I[WPWQXQXPWNUMRMONMQLTLWMYNZP[R[UZWW RRMPNNQMTMXNZ",
	2154: " 42H]ZFVTUXUZV[Y[[Y\\W R[FWTVXVZW[ RVTVQUNSMQMNNLQKTKWLYMZO[Q[SZUWVT RQMONMQLTLXMZ RWF[F",
	2155: " 26I[MVQUTTWRXPWNUMRMONMQLTLWMYNZP[R[UZWX RRMPNNQMTMXNZ",
	2156: " 35KZZGYHZI[H[GZFXFVGUHTJSMP[O_Na RXFVHUJTNRWQ[P^O`NaLbJbIaI`J_K`Ja ROMYM",
	2157: " 43H\\YMU[T^RaObLbJaI`I_J^K_J` RXMT[S^QaOb RVTVQUNSMQMNNLQKTKWLYMZO[Q[SZUWVT RQMONMQLTLXMZ",
	2158: " 31H]PFJ[ RQFK[ RMTOPQNSMUMWNXOXQVWVZW[ RUMWOWQUWUZV[Y[[Y\\W RMFQF",
	2159: " 26LYUFTGUHVGUF RMQNOPMSMTNTQRWRZS[ RRMSNSQQWQZR[U[WYXW",
	2160: " 32LYVFUGVHWGVF RNQOOQMTMUNUQR[Q^P`OaMbKbJaJ`K_L`Ka RSMTNTQQ[P^O`Mb",
	2161: " 34H\\PFJ[ RQFK[ RXNWOXPYOYNXMWMUNQROSMS ROSQTSZT[ ROSPTRZS[U[WZYW RMFQF",
	2162: " 18MYUFQTPXPZQ[T[VYWW RVFRTQXQZR[ RRFVF",
	2163: " 52AbBQCOEMHMINIPHTF[ RGMHNHPGTE[ RHTJPLNNMPMRNSOSQP[ RPMRORQO[ RRTTPVNXMZM\\N]O]Q[W[Z\\[ RZM\\O\\QZWZZ[[^[`YaW",
	2164: " 37F]GQHOJMMMNNNPMTK[ RLMMNMPLTJ[ RMTOPQNSMUMWNXOXQVWVZW[ RUMWOWQUWUZV[Y[[Y\\W",
	2165: " 32I[RMONMQLTLWMYNZP[R[UZWWXTXQWOVNTMRM RRMPNNQMTMXNZ RR[TZVWWTWPVN",
	2166: " 42G\\HQIOKMNMONOPNTJb RMMNNNPMTIb RNTOQQNSMUMWNXOYQYTXWVZS[Q[OZNWNT RWNXPXTWWUZS[ RFbMb",
	2167: " 33H\\XMRb RYMSb RVTVQUNSMQMNNLQKTKWLYMZO[Q[SZUWVT RQMONMQLTLXMZ RObVb",
	2168: " 26IZJQKOMMPMQNQPPTN[ ROMPNPPOTM[ RPTRPTNVMXMYNYOXPWOXN",
	2169: " 28J[XOXPYPYOXNUMRMONNONQORVVWW RNPOQVUWVWYVZS[P[MZLYLXMXMY",
	2170: " 18KYTFPTOXOZP[S[UYVW RUFQTPXPZQ[ RNMWM",
	2171: " 37F]GQHOJMMMNNNQLWLYN[ RLMMNMQKWKYLZN[P[RZTXVT RXMVTUXUZV[Y[[Y\\W RYMWTVXVZW[",
	2172: " 26H\\IQJOLMOMPNPQNWNYP[ RNMONOQMWMYNZP[Q[TZVXXUYQYMXMYO",
	2173: " 41C`DQEOGMJMKNKQIWIYK[ RIMJNJQHWHYIZK[M[OZQXRV RTMRVRYSZU[W[YZ[X\\V]R]M\\M]O RUMSVSYU[",
	2174: " 42H\\KQMNOMRMSOSR RQMRORRQVPXNZL[K[JZJYKXLYKZ RQVQYR[U[WZYW RYNXOYPZOZNYMXMVNTPSRRVRYS[",
	2175: " 41G\\HQIOKMNMONOQMWMYO[ RMMNNNQLWLYMZO[Q[SZUXWT RZMV[U^SaPbMbKaJ`J_K^L_K` RYMU[T^RaPb",
	2176: " 31H\\YMXOVQNWLYK[ RLQMOOMRMVO RMOONRNVOXO RLYNYRZUZWY RNYR[U[WYXW",
	2177: " 43G^VGUHVIWHWGUFRFOGMILLL[ RRFPGNIMLM[ R\\G[H\\I]H]G\\FZFXGWIW[ RZFYGXIX[ RIM[M RI[P[ RT[[[",
	2178: " 33G]WGVHWIXHWGUFRFOGMILLL[ RRFPGNIMLM[ RWMW[ RXMX[ RIMXM RI[P[ RT[[[",
	2179: " 35G]VGUHVIWHWGUF RXFRFOGMILLL[ RRFPGNIMLM[ RWHW[ RXFX[ RIMWM RI[P[ RT[[[",
	2180: " 54BcRGQHRISHRGPFMFJGHIGLG[ RMFKGIIHLH[ R]G\\H]I^H]G[FXFUGSIRLR[ RXFVGTISLS[ R]M][ R^M^[ RDM^M RD[K[ RO[V[ RZ[a[",
	2181: " 56BcRGQHRISHRGPFMFJGHIGLG[ RMFKGIIHLH[ R\\G[H\\I]H]G[F R^FXFUGSIRLR[ RXFVGTISLS[ R]H][ R^F^[ RDM]M RD[K[ RO[V[ RZ[a[",
	2182: " 12MXRMR[ RSMS[ ROMSM RO[V[",
	2184: " 25IZWNUMRMONMPLSLVMYNZQ[T[VZ RRMPNNPMSMVNYOZQ[ RMTUT",
	2185: " 43I\\TFQGOJNLMOLTLXMZO[Q[TZVWWUXRYMYIXGVFTF RTFRGPJOLNOMTMXNZO[ RQ[SZUWVUWRXMXIWGVF RNPWP",
	2186: " 42G]UFOb RVFNb RQMMNKPJSJVKXMZP[S[WZYXZUZRYPWNTMQM RQMNNLPKSKVLXNZP[ RS[VZXXYUYRXPVNTM",
	2187: " 27I[TMVNXPXOWNTMQMNNMOLQLSMUOWSZ RQMONNOMQMSNUSZT\\T^S_Q_",
	2190: " 45G]LMKNJPJRKUOYP[ RJRKTOXP[P]O`MbLbKaJ_J\\KXMTOQRNTMVMYNZPZTYXWZU[T[SZSXTWUXTY RVMXNYPYTXXWZ",
	2191: " 69E_YGXHYIZHYGWFTFQGOINKMNLRJ[I_Ha RTFRGPIOKNNLWK[J^I`HaFbDbCaC`D_E`Da R_G^H_I`H`G_F]F[GZHYJXMU[T_Sa R]F[HZJYNWWV[U^T`SaQbObNaN`O_P`Oa RIM^M",
	2192: " 52F^[GZH[I\\H[GXFUFRGPIOKNNMRK[J_Ia RUFSGQIPKONMWL[K^J`IaGbEbDaD`E_F`Ea RYMWTVXVZW[Z[\\Y]W RZMXTWXWZX[ RJMZM",
	2193: " 54F^YGXHYIZHZGXF R\\FUFRGPIOKNNMRK[J_Ia RUFSGQIPKONMWL[K^J`IaGbEbDaD`E_F`Ea R[FWTVXVZW[Z[\\Y]W R\\FXTWXWZX[ RJMYM",
	2194: " 86@cTGSHTIUHTGRFOFLGJIIKHNGRE[D_Ca ROFMGKIJKINGWF[E^D`CaAb?b>a>`?_@`?a R`G_H`IaH`G]FZFWGUITKSNRRP[O_Na RZFXGVIUKTNRWQ[P^O`NaLbJbIaI`J_K`Ja R^M\\T[X[Z\\[_[aYbW R_M]T\\X\\Z][ RDM_M",
	2195: " 88@cTGSHTIUHTGRFOFLGJIIKHNGRE[D_Ca ROFMGKIJKINGWF[E^D`CaAb?b>a>`?_@`?a R^G]H^I_H_G]F RaFZFWGUITKSNRRP[O_Na RZFXGVIUKTNRWQ[P^O`NaLbJbIaI`J_K`Ja R`F\\T[X[Z\\[_[aYbW RaF]T\\X\\Z][ RDM^M",
	2196: " 20LYMQNOPMSMTNTQRWRZS[ RRMSNSQQWQZR[U[WYXW",
	2200: " 40H\\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF RQFOGNHMJLOLRMWNYOZQ[ RS[UZVYWWXRXOWJVHUGSF",
	2201: " 11H\\NJPISFS[ RRGR[ RN[W[",
	2202: " 45H\\LJMKLLKKKJLHMGPFTFWGXHYJYLXNUPPRNSLUKXK[ RTFVGWHXJXLWNTPPR RKYLXNXSZVZXYYX RNXS[W[XZYXYV",
	2203: " 47H\\LJMKLLKKKJLHMGPFTFWGXIXLWNTOQO RTFVGWIWLVNTO RTOVPXRYTYWXYWZT[P[MZLYKWKVLUMVLW RWQXTXWWYVZT[",
	2204: " 13H\\THT[ RUFU[ RUFJUZU RQ[X[",
	2205: " 39H\\MFKP RKPMNPMSMVNXPYSYUXXVZS[P[MZLYKWKVLUMVLW RSMUNWPXSXUWXUZS[ RMFWF RMGRGWF",
	2206: " 48H\\WIVJWKXJXIWGUFRFOGMILKKOKULXNZQ[S[VZXXYUYTXQVOSNRNOOMQLT RRFPGNIMKLOLUMXOZQ[ RS[UZWXXUXTWQUOSN",
	2207: " 31H\\KFKL RKJLHNFPFUIWIXHYF RLHNGPGUI RYFYIXLTQSSRVR[ RXLSQRSQVQ[",
	2208: " 63H\\PFMGLILLMNPOTOWNXLXIWGTFPF RPFNGMIMLNNPO RTOVNWLWIVGTF RPOMPLQKSKWLYMZP[T[WZXYYWYSXQWPTO RPONPMQLSLWMYNZP[ RT[VZWYXWXSWQVPTO",
	2209: " 48H\\XMWPURRSQSNRLPKMKLLINGQFSFVGXIYLYRXVWXUZR[O[MZLXLWMVNWMX RQSORMPLMLLMIOGQF RSFUGWIXLXRWVVXTZR[",
	2210: "  6MWRYQZR[SZRY",
	2211: "  8MWR[QZRYSZS\\R^Q_",
	2212: " 12MWRMQNROSNRM RRYQZR[SZRY",
	2213: " 14MWRMQNROSNRM RR[QZRYSZS\\R^Q_",
	2214: " 15MWRFQHRTSHRF RRHRN RRYQZR[SZRY",
	2215: " 32I[MJNKMLLKLJMHNGPFSFVGWHXJXLWNVORQRT RSFUGVHWJWLVNTP RRYQZR[SZRY",
	2216: "  6NVRFQM RSFQM",
	2217: " 12JZNFMM ROFMM RVFUM RWFUM",
	2218: " 14KYQFOGNINKOMQNSNUMVKVIUGSFQF",
	2219: "  9JZRFRR RMIWO RWIMO",
	2220: "  3G][BIb",
	2221: " 20KYVBTDRGPKOPOTPYR]T`Vb RTDRHQKPPPTQYR\\T`",
	2222: " 20KYNBPDRGTKUPUTTYR]P`Nb RPDRHSKTPTTSYR\\P`",
	2223: " 12KYOBOb RPBPb ROBVB RObVb",
	2224: " 12KYTBTb RUBUb RNBUB RNbUb",
	2225: " 40KYTBRCQDPFPHQJRKSMSOQQ RRCQEQGRISJTLTNSPORSTTVTXSZR[Q]Q_Ra RQSSUSWRYQZP\\P^Q`RaTb",
	2226: " 40KYPBRCSDTFTHSJRKQMQOSQ RRCSESGRIQJPLPNQPURQTPVPXQZR[S]S_Ra RSSQUQWRYSZT\\T^S`RaPb",
	2227: "  4KYUBNRUb",
	2228: "  4KYOBVROb",
	2229: "  3NVRBRb",
	2230: "  6KYOBOb RUBUb",
	2231: "  3E_IR[R",
	2232: "  6E_RIR[ RIR[R",
	2233: "  9F^RJR[ RJRZR RJ[Z[",
	2234: "  9F^RJR[ RJJZJ RJRZR",
	2235: "  6G]KKYY RYKKY",
	2236: "  6MWRQQRRSSRRQ",
	2237: " 15E_RIQJRKSJRI RIR[R RRYQZR[SZRY",
	2238: "  6E_IO[O RIU[U",
	2239: "  9E_YIK[ RIO[O RIU[U",
	2240: "  9E_IM[M RIR[R RIW[W",
	2241: "  4F^ZIJRZ[",
	2242: "  4F^JIZRJ[",
	2243: " 10F^ZFJMZT RJVZV RJ[Z[",
	2244: " 10F^JFZMJT RJVZV RJ[Z[",
	2245: " 21F_[WYWWVUTRPQOONMNKOJQJSKUMVOVQURTUPWNYM[M",
	2246: " 24F^IUISJPLONOPPTSVTXTZS[Q RISJQLPNPPQTTVUXUZT[Q[O",
	2247: "  8G]JTROZT RJTRPZT",
	2248: "  7LXTFOL RTFUGOL",
	2249: "  7LXPFUL RPFOGUL",
	2250: " 18H\\KFLHNJQKSKVJXHYF RKFLINKQLSLVKXIYF",
	2251: "  8MWRHQGRFSGSIRKQL",
	2252: "  8MWSFRGQIQKRLSKRJ",
	2253: "  8MWRHSGRFQGQIRKSL",
	2254: "  8MWQFRGSISKRLQKRJ",
	2255: " 10E[HMLMRY RKMR[ R[BR[",
	2256: " 13F^ZJSJOKMLKNJQJSKVMXOYSZZZ",
	2257: " 13F^JJJQKULWNYQZSZVYXWYUZQZJ",
	2258: " 13F^JJQJUKWLYNZQZSYVWXUYQZJZ",
	2259: " 13F^JZJSKOLMNKQJSJVKXMYOZSZZ",
	2260: " 16F^ZJSJOKMLKNJQJSKVMXOYSZZZ RJRVR",
	2261: " 11E_XP[RXT RUMZRUW RIRZR",
	2262: " 11JZPLRITL RMORJWO RRJR[",
	2263: " 11E_LPIRLT ROMJROW RJR[R",
	2264: " 11JZPXR[TX RMURZWU RRIRZ",
	2265: " 44I\\XRWOVNTMRMONMQLTLWMYNZP[R[UZWXXUYPYKXHWGUFRFPGOHOIPIPH RRMPNNQMTMXNZ RR[TZVXWUXPXKWHUF",
	2266: " 15H\\JFR[ RKFRY RZFR[ RJFZF RKGYG",
	2267: " 10AbDMIMRY RHNR[ Rb:R[",
	2268: " 32F^[CZD[E\\D\\C[BYBWCUETGSJRNPZO^N` RVDUFTJRVQZP]O_MaKbIbHaH`I_J`Ia",
	2269: " 50F^[CZD[E\\D\\C[BYBWCUETGSJRNPZO^N` RVDUFTJRVQZP]O_MaKbIbHaH`I_J`Ia RQKNLLNKQKSLVNXQYSYVXXVYSYQXNVLSKQK",
	2270: " 26F_\\S[UYVWVUUTTQPPONNLNJOIQISJULVNVPUQTTPUOWNYN[O\\Q\\S",
	2271: " 32F^[FI[ RNFPHPJOLMMKMIKIIJGLFNFPGSHVHYG[F RWTUUTWTYV[X[ZZ[X[VYTWT",
	2272: " 49F_[NZO[P\\O\\N[MZMYNXPVUTXRZP[M[JZIXIUJSPORMSKSIRGPFNGMIMKNNPQUXWZZ[[[\\Z\\Y RM[KZJXJUKSMQ RMKNMVXXZZ[",
	2273: " 56E`WNVLTKQKOLNMMPMSNUPVSVUUVS RQKOMNPNSOUPV RWKVSVUXVZV\\T]Q]O\\L[JYHWGTFQFNGLHJJILHOHRIUJWLYNZQ[T[WZYYZX RXKWSWUXV",
	2274: " 42H\\PBP_ RTBT_ RXIWJXKYJYIWGTFPFMGKIKKLMMNOOUQWRYT RKKMMONUPWQXRYTYXWZT[P[MZKXKWLVMWLX",
	2275: " 12H]SFLb RYFRb RLQZQ RKWYW",
	2276: " 46JZUITJUKVJVIUGSFQFOGNINKOMQOVR ROMTPVRWTWVVXTZ RPNNPMRMTNVPXU[ RNVSYU[V]V_UaSbQbOaN_N^O]P^O_",
	2277: " 30JZRFQHRJSHRF RRFRb RRQQTRbSTRQ RLMNNPMNLLM RLMXM RTMVNXMVLTM",
	2278: " 56JZRFQHRJSHRF RRFRT RRPQRSVRXQVSRRP RRTRb RR^Q`RbS`R^ RLMNNPMNLLM RLMXM RTMVNXMVLTM RL[N\\P[NZL[ RL[X[ RT[V\\X[VZT[",
	2279: " 12I\\XFX[ RKFXF RPPXP RK[X[",
	2281: " 38E`QFNGKIILHOHRIUKXNZQ[T[WZZX\\U]R]O\\LZIWGTFQF RROQPQQRRSRTQTPSORO RRPRQSQSPRP",
	2282: " 45J[PFNGOIQJ RPFOGOI RUFWGVITJ RUFVGVI RQJOKNLMNMQNSOTQUTUVTWSXQXNWLVKTJQJ RRUR[ RSUS[ RNXWX",
	2283: " 27I\\RFOGMILLLMMPORRSSSVRXPYMYLXIVGSFRF RRSR[ RSSS[ RNWWW",
	2284: " 28D`PFMGJIHLGOGSHVJYM[P\\T\\W[ZY\\V]S]O\\LZIWGTFPF RRFR\\ RGQ]Q",
	2285: " 31G`PMMNKPJSJTKWMYPZQZTYVWWTWSVPTNQMPM R]GWG[HUN R]G]M\\IVO R\\HVN",
	2286: " 28F\\IIJGLFOFQGRIRLQOPQNSKU ROFPGQIQMPPNS RVFT[ RWFS[ RKUYU",
	2287: " 30I\\MFMU RNFMQ RMQNOONQMTMWNXPXRWTUV RTMVNWPWRTXTZU[W[YY RKFNF",
	2288: " 44I\\RNOOMQLTLUMXOZR[S[VZXXYUYTXQVOSNRN RRHNJRFRN RSHWJSFSN RRSQTQURVSVTUTTSSRS RRTRUSUSTRT",
	2289: " 37G^QHRFR[ RTHSFS[ RJHKFKMLPNRQSRS RMHLFLNMQ R[HZFZMYPWRTSSS RXHYFYNXQ RNWWW",
	2290: " 31G]LFL[ RMFM[ RIFUFXGYHZJZMYOXPUQMQ RUFWGXHYJYMXOWPUQ RI[Y[YVX[",
	2291: " 24H[YGUGQHNJLMKPKSLVNYQ[U\\Y\\ RYGVHSJQMPPPSQVSYV[Y\\",
	2292: " 27F_OQMQKRJSIUIWJYKZM[O[QZRYSWSURSQROQ RSHPQ RZJRR R\\QST",
	2293: " 12H\\OKUY RUKOY RKOYU RYOKU",
	2294: " 48F^NVLUKUIVHXHYI[K\\L\\N[OYOXNVKRJOJMKJMHPGTGWHYJZMZOYRVVUXUYV[X\\Y\\[[\\Y\\X[VYUXUVV RJMKKMIPHTHWIYKZM",
	2295: " 48F^NMLNKNIMHKHJIHKGLGNHOJOKNMKQJTJVKYM[P\\T\\W[YYZVZTYQVMUKUJVHXGYG[H\\J\\K[MYNXNVM RJVKXMZP[T[WZYXZV",
	2301: " 40F_JMILIJJHLGNGPHQIRKSP RIJKHMHOIPJQLRPR[ R[M\\L\\J[HYGWGUHTISKRP R\\JZHXHVIUJTLSPS[",
	2302: " 51F^IGJKKMMOPPTPWOYMZK[G RIGJJKLMNPOTOWNYLZJ[G RPONPMQLSLVMXOZQ[S[UZWXXVXSWQVPTO RPPNQMSMVNY RVYWVWSVQTP",
	2303: " 30F^MJMV RNKNU RVKVU RWJWV RIGKIMJPKTKWJYI[G RIYKWMVPUTUWVYW[Y",
	2304: " 48F^[ILIJJILINJPLQNQPPQNQLPJ[J RIMJOKPMQ RQMPKOJMI RIXXXZW[U[SZQXPVPTQSSSUTWIW R[TZRYQWP RSTTVUWWX",
	2305: " 48F]OUMTLTJUIWIXJZL[M[OZPXPWOUJPINIKJILHOGSGWHYJZLZOYRVUUWUYV[X[YZZX RMSKPJNJKKILH RSGVHXJYLYOXRVU",
	2306: " 48G_HKKHMKMV RJILLLV RMKPHRKRU ROIQLQU RRKUHWKW[ RTIVLV[ RWKZH[J\\M\\P[SZUXWUYP[ RYIZJ[M[PZSYUWWTYP[",
	2307: " 41F^ISMSLRKOKMLJNHQGSGVHXJYMYOXRWS[S RITOTMRLOLMMJOHQG RSGUHWJXMXOWRUT[T RKXYX RKYYY",
	2308: " 30F_GLJIMLMX RIJLMLX RMLPISLSX ROJRMRX RSLVIYLYW[Y RUJXMXXZZ]W",
	2309: " 33G]ZIJY RZIWJQJ RXKUKQJ RZIYLYR RXKXNYR RQRJR RPSMSJR RQRQY RPSPVQY",
	2310: " 33F^HOJKOU RJMOWRPWPZO[M[KZIXHWHUITKTMUPVRWUWXUZ RWHVIUKUMWQXTXWWYUZ",
	2311: " 36F^IOLLPN RKMOORLUN RQMTOWLYN RVMXO[L RIULRPT RKSOURRUT RQSTUWRYT RVSXU[R",
	2312: " 48F^JHNJPLQOQRPUNWJY RJHMIOJQLRO RRRQUOWMXJY RZHWIUJSLRO RRRSUUWWXZY RZHVJTLSOSRTUVWZY RIP[P RIQ[Q",
	2317: " 12NVQQQSSSSQQQ RQQSS RSQQS",
	2318: " 18JZMPQRTTVVWYW[V]U^ RMQST RMRPSTUVWWY",
	2319: " 18JZWKVMTOPQMR RSPMS RUFVGWIWKVNTPQRMT",
	2320: " 36H\\SMONLPKRKTLVNWQWUVXTYRYPXNVMSM RXNSM RVMQNLP RONKR RLVQW RNWSVXT RUVYR",
	2321: " 36H\\SMONLPKRKTLVNWQWUVXTYRYPXNVMSM RXNSM RVMQNLP RONKR RLVQW RNWSVXT RUVYR",
	2322: " 34J[SMPNNPMRMTNVPWRWUVWTXRXPWNUMSM ROPUM RNRVN RMTWO RNUXP ROVWR RPWVT",
	2323: " 18JZOGO^ RUFU] RMNWL RMOWM RMWWU RMXWV",
	2324: " 18JZNFNX RVLV^ RNNVL RNOVM RNWVU RNXVV",
	2325: " 25JZNBNW RNNQLTLVMWOWQVSSUQVNW RNNQMTMVN RUMVOVQUSSU",
	2326: " 18E_HIHL R\\I\\L RHI\\I RHJ\\J RHK\\K RHL\\L",
	2327: " 18JZMNMQ RWNWQ RMNWN RMOWO RMPWP RMQWQ",
	2328: " 49JZMLWX RMLONQOTOVNWMWKUKUMTO RONTO RQOWM RVKVN RULWL RWXUVSUPUNVMWMYOYOWPU RUVPU RSUMW RNVNY RMXOX",
	2329: " 26JZPOOMOKMKMMNNPOSOUNWL RNKNN RMLOL RMMSO RPOUN RWLWY",
	2330: " 86A^GfHfIeIdHcGcFdFfGhIiKiNhPfQdR`RUQ;Q4R/S-U,V,X-Y/Y3X6W8U;P?JCHEFHEJDNDREVGYJ[N\\R\\V[XZZW[T[PZMYKWITHPHMIKKJNJRKUMW RGdGeHeHdGd RU;Q?LCIFGIFKENERFVGXJ[ RR\\U[WZYWZTZPYMXKVITH",
	2331: "103EfNSOUQVSVUUVSVQUOSNQNOONPMSMVNYP[S\\V\\Y[[Y\\W]T]P\\MZJXIUHRHOIMJKLIOHSHXI]KaMcPeTfYf]e`cba RKLJNIRIXJ\\L`NbQdUeYe]d_cba RPOTO ROPUP RNQVQ RNRVR RNSVS ROTUT RPUTU RaLaNcNcLaL RbLbN RaMcM RaVaXcXcVaV RbVbX RaWcW",
	2332: " 30D`H@Hd RM@Md RW@Wd R\\@\\d RMMWK RMNWL RMOWM RMWWU RMXWV RMYWW",
	2367: " 12NVQQQSSSSQQQ RQQSS RSQQS",
	2368: " 18JZMPQRTTVVWYW[V]U^ RMQST RMRPSTUVWWY",
	2369: " 18JZWKVMTOPQMR RSPMS RUFVGWIWKVNTPQRMT",
	2370: " 32H\\PMMNLOKQKSLUMVPWTWWVXUYSYQXOWNTMPM RMNLPLSMUNVPW RWVXTXQWOVNTM",
	2371: " 36H\\SMONLPKRKTLVNWQWUVXTYRYPXNVMSM RXNSM RVMQNLP RONKR RLVQW RNWSVXT RUVYR",
	2372: " 34J[SMPNNPMRMTNVPWRWUVWTXRXPWNUMSM ROPUM RNRVN RMTWO RNUXP ROVWR RPWVT",
	2373: " 18JZOGO^ RUFU] RMNWL RMOWM RMWWU RMXWV",
	2374: " 18JZNFNX RVLV^ RNNVL RNOVM RNWVU RNXVV",
	2375: " 25JZNBNW RNNQLTLVMWOWQVSSUQVNW RNNQMTMVN RUMVOVQUSSU",
	2376: " 18E_HIHL R\\I\\L RHI\\I RHJ\\J RHK\\K RHL\\L",
	2377: " 18JZMNMQ RWNWQ RMNWN RMOWO RMPWP RMQWQ",
	2378: " 36JZQCVMRTRU RULQS RTITKPRRUUY RW\\UYSXQXOYN[N]O_Ra RW\\UZSYOYO]P_Ra RSXPZN]",
	2379: " 26JZPOOMOKMKMMNNPOSOUNWL RNKNN RMLOL RMMSO RPOUN RWLSY",
	2380: " 86A^GfHfIeIdHcGcFdFfGhIiKiNhPfQdR`RUQ;Q4R/S-U,V,X-Y/Y3X6W8U;P?JCHEFHEJDNDREVGYJ[N\\R\\V[XZZW[T[PZMYKWITHPHMIKKJNJRKUMW RGdGeHeHdGd RU;Q?LCIFGIFKENERFVGXJ[ RR\\U[WZYWZTZPYMXKVITH",
	2381: " 89IjNQOOQNSNUOVQVSUUSVQVOUNTMQMNNKPISHWH[I^K`NaRaW`[_]]`ZcVfQiMk RWHZI]K_N`R`W_[^]\\`YcTgQi RPOTO ROPUP RNQVQ RNRVR RNSVS ROTUT RPUTU ReLeNgNgLeL RfLfN ReMgM ReVeXgXgVeV RfVfX ReWgW",
	2382: " 85D`H>Hf RI>If RM>Mf RQBSBSDQDQAR?T>W>Y?[A\\D\\I[LYNWOUOSNRLQNOQNROSQVRXSVUUWUYV[X\\[\\`[cYeWfTfReQcQ`S`SbQb RRBRD RQCSC RY?ZA[D[IZLYN RRLRNPQNRPSRVRX RYVZX[[[`ZcYe RR`Rb RQaSa",
	2401: " 21AcHBHb RIBIb R[B[b R\\B\\b RDB`B RDbMb RWb`b",
	2402: " 23BaGBQPFb RFBPP REBPQ REB\\B^I[B RGa\\a RFb\\b^[[b",
	2403: " 28I[X+U1R8P=OANFMNMVN^OcPgRlUsXy RU1S6Q<P@OFNNNVO^PdQhSnUs",
	2404: " 28I[L+O1R8T=UAVFWNWVV^UcTgRlOsLy RO1Q6S<T@UFVNVVU^TdShQnOs",
	2405: " 14I[M+MRMy RN+NRNy RM+X+ RMyXy",
	2406: " 14I[V+VRVy RW+WRWy RL+W+ RLyWy",
	2407: " 48I[V+S-Q/P1O4O8P<TDUGUJTMRP RS-Q0P4P8Q;UCVGVJUMRPNRRTUWVZV]UaQiPlPpQtSw RRTTWUZU]T`PhOlOpPsQuSwVy",
	2408: " 48I[N+Q-S/T1U4U8T<PDOGOJPMRP RQ-S0T4T8S;OCNGNJOMRPVRRTOWNZN]OaSiTlTpStQw RRTPWOZO]P`ThUlUpTsSuQwNy",
	2409: " 32I[V.S1Q4O8N=NCOIPMSXT\\UbUgTlSoQs RS1Q5P8O=OBPHQLTWU[VaVgUlSpQsNv",
	2410: " 32I[N.Q1S4U8V=VCUITMQXP\\ObOgPlQoSs RQ1S5T8U=UBTHSLPWO[NaNgOlQpSsVv",
	2411: " 147Z:RARRo R@RQo R?RRr RZ\"VJRr",
	2412: " 57Ca].\\.[/[0\\1]1^0^.],[+Y+W,U.T0S3R:QJQjPsOv R\\/\\0]0]/\\/ RR:Rj RU.T1S:SZRjQqPtOvMxKyIyGxFvFtGsHsItIuHvGv RGtGuHuHtGt",
	2501: " 20H\\RFJ[ RRIK[J[ RRIY[Z[ RRFZ[ RMUWU RLVXV",
	2502: " 44H\\LFL[ RMGMZ RLFTFWGXHYJYMXOWPTQ RMGTGWHXJXMWOTP RMPTPWQXRYTYWXYWZT[L[ RMQTQWRXTXWWYTZMZ",
	2503: " 38H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZV RZKYKXIWHUGQGOHMKLNLSMVOYQZUZWYXXYVZV",
	2504: " 32H]LFL[ RMGMZ RLFSFVGXIYKZNZSYVXXVZS[L[ RMGSGVHWIXKYNYSXVWXVYSZMZ",
	2505: " 27I\\MFM[ RNGNZ RMFYF RNGYGYF RNPTPTQ RNQTQ RNZYZY[ RM[Y[",
	2506: " 21I[MFM[ RNGN[M[ RMFYF RNGYGYF RNPTPTQ RNQTQ",
	2507: " 44H]ZKYIWGUFQFOGMILKKNKSLVMXOZQ[U[WZYXZVZRUR RZKYKXIWHUGQGOHNIMKLNLSMVNXOYQZUZWYXXYVYSUSUR",
	2508: " 22G]KFK[ RKFLFL[K[ RYFXFX[Y[ RYFY[ RLPXP RLQXQ",
	2509: "  8NWRFR[S[ RRFSFS[",
	2510: " 20J[VFVVUYSZQZOYNVMV RVFWFWVVYUZS[Q[OZNYMV",
	2511: " 22H]LFL[M[ RLFMFM[ RZFYFMR RZFMS RPOY[Z[ RQOZ[",
	2512: " 14IZMFM[ RMFNFNZ RNZYZY[ RM[Y[",
	2513: " 26F^JFJ[ RKKK[J[ RKKR[ RJFRX RZFRX RYKR[ RYKY[Z[ RZFZ[",
	2514: " 20G]KFK[ RLIL[K[ RLIY[ RKFXX RXFXX RXFYFY[",
	2515: " 40G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF RQGNHLKKNKSLVNYQZSZVYXVYSYNXKVHSGQG",
	2516: " 27H\\LFL[ RMGM[L[ RLFUFWGXHYJYMXOWPUQMQ RMGUGWHXJXMWOUPMP",
	2517: " 48G]PFNGLIKKJNJSKVLXNZP[T[VZXXYVZSZNYKXIVGTFPF RQGNHLKKNKSLVNYQZSZVYXVYSYNXKVHSGQG RSXX]Y] RSXTXY]",
	2518: " 34H\\LFL[ RMGM[L[ RLFTFWGXHYJYMXOWPTQMQ RMGTGWHXJXMWOTPMP RRQX[Y[ RSQY[",
	2519: " 43H\\YIWGTFPFMGKIKKLMMNOOTQVRWSXUXXWYTZPZNYMXKX RYIWIVHTGPGMHLILKMMONTPVQXSYUYXWZT[P[MZKX",
	2520: " 15J[RGR[ RSGS[R[ RLFYFYG RLFLGYG",
	2521: " 24G]KFKULXNZQ[S[VZXXYUYF RKFLFLUMXNYQZSZVYWXXUXFYF",
	2522: " 14H\\JFR[ RJFKFRX RZFYFRX RZFR[",
	2523: " 26E_GFM[ RGFHFMX RRFMX RRIM[ RRIW[ RRFWX R]F\\FWX R]FW[",
	2524: " 16H\\KFX[Y[ RKFLFY[ RYFXFK[ RYFL[K[",
	2525: " 17I\\KFRPR[S[ RKFLFSP RZFYFRP RZFSPS[",
	2526: " 20H\\XFK[ RYFL[ RKFYF RKFKGXG RLZYZY[ RK[Y[",
	2551: " 38E\\XFVHTKQPOSLWIZG[E[DZDXEWFXEY RXFWJUTT[ RXFU[ RT[TYSVRTPRNQLQKRKTLWOZR[V[XZ",
	2552: " 70F^UGTHSJQOOUNWLZJ[ RTHSKQSPVOXMZJ[H[GZGXHWIXHY ROLNNMOKOJNJLKJMHOGRFXFZG[I[KZMXNTORO RXFYGZIZKYMXN RTOWPXQYSYVXYWZU[S[RZRXSU RTOVPWQXSXVWYU[",
	2553: " 41H]KHJJJLKNNOQOUNWMYKZIZGYFWFTGQJOMMQLULXMZP[R[UZWXXVXTWRURSSRU RWFUGRJPMNQMUMXNZP[",
	2554: " 43F]UGTHSJQOOUNWLZJ[ RTHSKQSPVOXMZJ[H[GZGXHWJWLXNZP[S[UZWXYTZOZLYIWGUFPFMGKIJKJMKNMNNMOK",
	2555: " 49I\\WIVJVLWMYMZKZIYGWFTFRGQHPJPLQNSO RTFRHQJQMSO RSOQONPLRKTKWLYMZO[R[UZWXXVXTWRURSSRU RQOOPMRLTLXMZ",
	2556: " 46G\\WHVJTORUQWOZM[ RQLPNNOLOKMKKLINGQF[FXGWHVKTSSVRXPZM[K[IZHYHXIWJXIY RSFWGXG ROSPRRQVQXPZMXT",
	2557: " 53G]JIIKIMJOLPOPROTNWKXHXGWFVFTGRIQKPNPQQSSTUTWSYQZO RWFUGSIRKQNQRST RZOYSWWUYSZO[L[JZIXIWJVKWJX RYSWVUXRZO[",
	2558: " 55F^LLKKKILGOFRFOQMWLYKZI[G[FZFXGWHXGY RRFOONRLWKYI[ RJTKSMRVOXN[L]J^H^G]F\\FZGXJWLURTVTYV[W[YZ[X R\\FZHXLVRUVUYV[",
	2559: " 33IYWHUKSPQUPWNZL[ RYLWNTOQOONNLNJOHQGUFYFWHVJTPRVQXOZL[J[IZIXJWKXJY",
	2560: " 34IZYFWHUKSPPYN] RYMWOTPQPOONMNKOIQGUFYFWIVKSTQXPZN]M^K_J^J\\KZMXOWRVVU",
	2561: " 59F^LLKKKIMGPFRFOQMWLYKZI[G[FZFXGWHXGY RRFOONRLWKYI[ RZGWKUMSNPO R]G\\H]I^H^G]F\\FZGWLVMTNPO RPOSPTRUYV[ RPORPSRTYV[W[YZ[X",
	2562: " 40I[MILKLMMOOPRPUOWNZK[H[GZFYFWGVHTKPUOWMZK[ RVHTLRSQVPXNZK[I[HZHXIWKWMXPZR[U[WZYX",
	2563: " 49D`RFNOKUIXGZE[C[BZBXCWDXCY RRFPMOQNVNZP[ RRFQJPOOVOZP[ R[FWORXP[ R[FYMXQWVWZY[Z[\\Z^X R[FZJYOXVXZY[",
	2564: " 38G^RFQJOPMULWJZH[F[EZEXFWGXFY RRFRKSVT[ RRFSKTVT[ R`G_H`IaHaG`F^F\\GZJYLWQUWT[",
	2565: " 34H]SFQGOIMLLNKRKVLYMZO[Q[TZVXXUYSZOZKYHXGWGUHSJQNPSPV RQGOJMNLRLVMYO[",
	2566: " 53F]UGTHSJQOOUNWLZJ[ RTHSKQSPVOXMZJ[H[GZGXHWIXHY ROLNNMOKOJNJLKJMHOGRFVFYGZH[J[MZOYPVQTQRP RVFXGYHZJZMYOXPVQ",
	2567: " 43H]UJULTNSOQPOPNNNLOIQGTFWFYGZIZMYPWSSWPYNZK[I[HZHXIWKWMXPZS[V[XZZX RWFXGYIYMXPVSSVOYK[",
	2568: " 65F^UGTHSJQOOUNWLZJ[ RTHSKQSPVOXMZJ[H[GZGXHWIXHY ROLNNMOKOJNJLKJMHOGRFWFZG[I[KZMYNVORO RWFYGZIZKYMXNVO RROUPVRWYX[ RROTPURVYX[Y[[Z]X",
	2569: " 36H\\NIMKMMNOPPSPVOXN[K\\H\\G[FZFXGWHVJUMSTRWPZN[ RVJUNTUSXQZN[K[IZHXHWIVJWIX",
	2570: " 38I[YHXJVOTUSWQZO[ RSLRNPONOMMMKNIPGSF\\FZGYHXKVSUVTXRZO[M[KZJYJXKWLXKY RUFYGZG",
	2571: " 39G]HJJGLFMFOHOKNNKVKYL[ RMFNHNKKSJVJYL[N[PZSWUTVR RZFVRUVUYW[X[ZZ\\X R[FWRVVVYW[",
	2572: " 36G\\HJJGLFMFOHOKNOLVLYM[ RMFNHNKLRKVKYM[N[QZTWVTXPYMZIZGYFXFWGVIVLWNYP[Q]Q",
	2573: " 41F]ILHLGKGIHGJFNFMHLLKUJ[ RLLLUK[ RVFTHRLOUMYK[ RVFUHTLSUR[ RTLTUS[ R`F^G\\IZLWUUYS[",
	2574: " 52H\\PKOLMLLKLIMGOFQFSGTITLSPQUOXMZJ[H[GZGXHWIXHY RQFRGSISLRPPUNXLZJ[ R]G\\H]I^H^G]F[FYGWIULSPRURXSZT[U[WZYX",
	2575: " 42G]JJLGNFOFQGQIOOORPT ROFPGPINONRPTRTUSWQYNZL R\\FZLWTUX R]F[LYQWUUXSZP[L[JZIXIWJVKWJX",
	2576: " 44G\\ZHYJWOVRUTSWQYOZL[ RSLRNPONOMMMKNIPGSF]F[GZHYKXOVUTXQZL[H[GZGXHWJWLXOZQ[T[WZYX RVFZG[G",
	2601: " 36H\\WMW[X[ RWMXMX[ RWPUNSMPMNNLPKSKULXNZP[S[UZWX RWPSNPNNOMPLSLUMXNYPZSZWX",
	2602: " 36H\\LFL[M[ RLFMFM[ RMPONQMTMVNXPYSYUXXVZT[Q[OZMX RMPQNTNVOWPXSXUWXVYTZQZMX",
	2603: " 32I[XPVNTMQMONMPLSLUMXOZQ[T[VZXX RXPWQVOTNQNOONPMSMUNXOYQZTZVYWWXX",
	2604: " 36H\\WFW[X[ RWFXFX[ RWPUNSMPMNNLPKSKULXNZP[S[UZWX RWPSNPNNOMPLSLUMXNYPZSZWX",
	2605: " 36I[MTXTXQWOVNTMQMONMPLSLUMXOZQ[T[VZXX RMSWSWQVOTNQNOONPMSMUNXOYQZTZVYWWXX",
	2606: " 24LZWFUFSGRJR[S[ RWFWGUGSH RTGSJS[ ROMVMVN ROMONVN",
	2607: " 48H\\XMWMW\\V_U`SaQaO`N_L_ RXMX\\W_UaSbPbNaL_ RWPUNSMPMNNLPKSKULXNZP[S[UZWX RWPSNPNNOMPLSLUMXNYPZSZWX",
	2608: " 25H\\LFL[M[ RLFMFM[ RMQPNRMUMWNXQX[ RMQPORNTNVOWQW[X[",
	2609: " 24NWRFQGQHRISITHTGSFRF RRGRHSHSGRG RRMR[S[ RRMSMS[",
	2610: " 24NWRFQGQHRISITHTGSFRF RRGRHSHSGRG RRMRbSb RRMSMSb",
	2611: " 22H[LFL[M[ RLFMFM[ RXMWMMW RXMMX RPTV[X[ RQSX[",
	2612: "  8NWRFR[S[ RRFSFS[",
	2613: " 42CbGMG[H[ RGMHMH[ RHQKNMMPMRNSQS[ RHQKOMNONQORQR[S[ RSQVNXM[M]N^Q^[ RSQVOXNZN\\O]Q][^[",
	2614: " 25H\\LML[M[ RLMMMM[ RMQPNRMUMWNXQX[ RMQPORNTNVOWQW[X[",
	2615: " 36I\\QMONMPLSLUMXOZQ[T[VZXXYUYSXPVNTMQM RQNOONPMSMUNXOYQZTZVYWXXUXSWPVOTNQN",
	2616: " 36H\\LMLbMb RLMMMMb RMPONQMTMVNXPYSYUXXVZT[Q[OZMX RMPQNTNVOWPXSXUWXVYTZQZMX",
	2617: " 36H\\WMWbXb RWMXMXb RWPUNSMPMNNLPKSKULXNZP[S[UZWX RWPSNPNNOMPLSLUMXNYPZSZWX",
	2618: " 21KYOMO[P[ ROMPMP[ RPSQPSNUMXM RPSQQSOUNXNXM",
	2619: " 50J[XPWNTMQMNNMPNRPSUUWV RVUWWWXVZ RWYTZQZNY ROZNXMX RXPWPVN RWOTNQNNO RONNPOR RNQPRUTWUXWXXWZT[Q[NZMX",
	2620: " 16MXRFR[S[ RRFSFS[ ROMVMVN ROMONVN",
	2621: " 25H\\LMLWMZO[R[TZWW RLMMMMWNYPZRZTYWW RWMW[X[ RWMXMX[",
	2622: " 14JZLMR[ RLMMMRY RXMWMRY RXMR[",
	2623: " 26F^IMN[ RIMJMNX RRMNX RRPN[ RRPV[ RRMVX R[MZMVX R[MV[",
	2624: " 16I[LMW[X[ RLMMMX[ RXMWML[ RXMM[L[",
	2625: " 17JZLMR[ RLMMMRY RXMWMRYNb RXMR[ObNb",
	2626: " 20I[VNL[ RXMNZ RLMXM RLMLNVN RNZXZX[ RL[X[",
	2651: " 33K[UUTSRRPRNSMTLVLXMZO[Q[SZTX RPRNTMVMYO[ RVRTXTZV[XZYY[V RWRUXUZV[",
	2652: " 23LZLVNSPO RSFMXMZO[P[RZTXUUURVVWWXWZV RTFNXNZO[",
	2653: " 22LXTSSTTTTSSRQROSNTMVMXNZP[S[VYXV RQROTNVNYP[",
	2654: " 33K[UUTSRRPRNSMTLVLXMZO[Q[SZTX RPRNTMVMYO[ RZFTXTZV[XZYY[V R[FUXUZV[",
	2655: " 23LXOYQXRWSUSSRRQROSNTMVMXNZP[S[VYXV RQROTNVNYP[",
	2656: " 27OXRRUOWLXIXGWFUGTIKdKfLgNfOcPZQ[S[UZVYXV RTISNRRO[M`Kd",
	2657: " 38K[UUTSRRPRNSMTLVLXMZO[Q[SZTX RPRNTMVMYO[ RVRPd RWRT[R`PdOfMgLfLdMaO_R]V[YY[V",
	2658: " 30L[LVNSPO RSFL[ RTFM[ ROUQSSRTRVSVUUXUZV[ RTRUSUUTXTZV[XZYY[V",
	2659: " 19NVSLRMSNTMSL RQROXOZQ[SZTYVV RRRPXPZQ[",
	2660: " 24NVSLRMSNTMSL RQRKd RRRO[M`KdJfHgGfGdHaJ_M]Q[TYVV",
	2661: " 31LZLVNSPO RSFL[ RTFM[ RURUSVSURTRRTOU ROURVSZT[ ROUQVRZT[U[XYZV",
	2662: " 17NVNVPSRO RUFOXOZQ[SZTYVV RVFPXPZQ[",
	2663: " 45E^EVGSIRKSKUI[ RIRJSJUH[ RKUMSORPRRSRUP[ RPRQSQUO[ RRUTSVRWRYSYUXXXZY[ RWRXSXUWXWZY[[Z\\Y^V",
	2664: " 32I[IVKSMROSOUM[ RMRNSNUL[ ROUQSSRTRVSVUUXUZV[ RTRUSUUTXTZV[XZYY[V",
	2665: " 29KYRRPRNSMTLVLXMZO[Q[SZTYUWUUTSRRQSQURWTXVXXWYV RPRNTMVMYO[",
	2666: " 30L[LVNSPO RQLHg RRLIg ROUQSSRTRVSVUUXUZV[ RTRUSUUTXTZV[XZYY[V",
	2667: " 35K[UUTSRRPRNSMTLVLXMZO[Q[SZ RPRNTMVMYO[ RVRPdPfQgSfTcT[V[YY[V RWRT[R`Pd",
	2668: " 24LZLVNSPRRSRUP[ RPRQSQUO[ RRUTSVRWRVU RVRVUWWXWZV",
	2669: " 22NZNVPSQQQSTUUWUYTZR[ RQSSUTWTYR[ RNZP[U[XYZV",
	2670: " 20NVNVPSRO RUFOXOZQ[SZTYVV RVFPXPZQ[ RPNVN",
	2671: " 27K[NRLXLZN[O[QZSXUU RORMXMZN[ RVRTXTZV[XZYY[V RWRUXUZV[",
	2672: " 23KZNRMTLWLZN[O[RZTXUUUR RORNTMWMZN[ RURVVWWXWZV",
	2673: " 36H]LRJTIWIZK[L[NZPX RMRKTJWJZK[ RRRPXPZR[S[UZWXXUXR RSRQXQZR[ RXRYVZW[W]V",
	2674: " 42JZJVLSNRPRQSQUPXOZM[L[KZKYLYKZ RWSVTWTWSVRURSSRUQXQZR[U[XYZV RQSRU RSSQU RPXQZ RQXOZ",
	2675: " 32K[NRLXLZN[O[QZSXUU RORMXMZN[ RVRPd RWRT[R`PdOfMgLfLdMaO_R]V[YY[V",
	2676: " 38LYLVNSPRRRTSTVSXPZN[ RRRSSSVRXPZ RN[P\\Q^QaPdNfLgKfKdLaO^R\\VYYV RN[O\\P^PaOdNf",
	2700: " 42H\\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF ROGMJLOLRMWOZ RNYQZSZVY RUZWWXRXOWJUG RVHSGQGNH",
	2701: " 12H\\NJPISFS[ RNJNKPJRHR[S[",
	2702: " 34H\\LKLJMHNGPFTFVGWHXJXLWNUQL[ RLKMKMJNHPGTGVHWJWLVNTQK[ RLZYZY[ RK[Y[",
	2703: " 48H\\MFXFQO RMFMGWG RWFPO RQNSNVOXQYTYUXXVZS[P[MZLYKWLW RPOSOVPXS RTOWQXTXUWXTZ RXVVYSZPZMYLW ROZLX",
	2704: " 18H\\UIU[V[ RVFV[ RVFKVZV RUILV RLUZUZV",
	2705: " 53H\\MFLO RNGMN RMFWFWG RNGWG RMNPMSMVNXPYSYUXXVZS[P[MZLYKWLW RLOMOONSNVOXR RTNWPXSXUWXTZ RXVVYSZPZMYLW ROZLX",
	2706: " 62H\\VGWIXIWGTFRFOGMJLOLTMXOZR[S[VZXXYUYTXQVOSNRNOOMQ RWHTGRGOH RPGNJMOMTNXQZ RMVOYRZSZVYXV RTZWXXUXTWQTO RXSVPSOROOPMS RQONQMT",
	2707: " 12H\\KFYFO[ RKFKGXG RXFN[O[",
	2708: " 68H\\PFMGLILKMMNNPOTPVQWRXTXWWYTZPZMYLWLTMRNQPPTOVNWMXKXIWGTFPF RNGMIMKNMPNTOVPXRYTYWXYWZT[P[MZLYKWKTLRNPPOTNVMWKWIVG RWHTGPGMH RLXOZ RUZXX",
	2709: " 62H\\WPURRSQSNRLPKMKLLINGQFRFUGWIXMXRWWUZR[P[MZLXMXNZ RWMVPSR RWNUQRRQRNQLN RPRMPLMLLMIPG RLKNHQGRGUHWK RSGVIWMWRVWTZ RUYRZPZMY",
	2710: " 16MXRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	2711: " 24MXTZS[R[QZQYRXSXTYT\\S^Q_ RRYRZSZSYRY RS[T\\ RTZS^",
	2712: " 32MXRMQNQORPSPTOTNSMRM RRNROSOSNRN RRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	2713: " 40MXRMQNQORPSPTOTNSMRM RRNROSOSNRN RTZS[R[QZQYRXSXTYT\\S^Q_ RRYRZSZSYRY RS[T\\ RTZS^",
	2714: " 24MXRFRTST RRFSFST RRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	2715: " 58I\\LKLJMHNGQFTFWGXHYJYLXNWOUPRQ RLKMKMJNHQGTGWHXJXLWNUORP RMIPG RUGXI RXMTP RRPRTSTSP RRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	2716: " 24MXTFRGQIQLRMSMTLTKSJRJQK RRKRLSLSKRK RRGQK RQIRJ",
	2717: " 24MXTHSIRIQHQGRFSFTGTJSLQM RRGRHSHSGRG RSITJ RTHSL",
	2718: " 71F_\\MZMXNWPUVTXSYQZMZKYJWJUKSLRQOSMTKTISGQFPFNGMIMKNNPQUWXZZ[\\[ R\\M\\NZNXO RYNXPVVUXSZQ[M[KZJYIWIUJSLQQNRMSKSIRG RSHQGPGNH ROGNINKONQQVWXYZZ\\Z\\[",
	2719: " 51I\\RBR_S_ RRBSBS_ RWIYIWGTFQFNGLILKMMNNVRWSXUXWWYTZQZOYNX RWIVHTGQGNHMIMKNMVQXSYUYWXYWZT[Q[NZLXNX RXXUZ",
	2720: "  8G^[BIbJb R[B\\BJb",
	2721: " 24KYUBSDQGOKNPNTOYQ]S`UbVb RUBVBTDRGPKOPOTPYR]T`Vb",
	2722: " 24KYNBPDRGTKUPUTTYR]P`NbOb RNBOBQDSGUKVPVTUYS]Q`Ob",
	2723: " 39JZRFQGSQRR RRFRR RRFSGQQRR RMINIVOWO RMIWO RMIMJWNWO RWIVINOMO RWIMO RWIWJMNMO",
	2724: "  8F_JQ[Q[R RJQJR[R",
	2725: " 16F_RIRZSZ RRISISZ RJQ[Q[R RJQJR[R",
	2726: " 16F_JM[M[N RJMJN[N RJU[U[V RJUJV[V",
	2727: " 11NWSFRGRM RSGRM RSFTGRM",
	2728: " 22I[NFMGMM RNGMM RNFOGMM RWFVGVM RWGVM RWFXGVM",
	2729: " 30KYQFOGNINKOMQNSNUMVKVIUGSFQF RQFNIOMSNVKUGQF RSFOGNKQNUMVISF",
	2750: " 42H]TFQGOIMLLOKSKVLYMZO[Q[TZVXXUYRZNZKYHXGVFTF RTFRGPINLMOLSLVMYO[ RQ[SZUXWUXRYNYKXHVF",
	2751: " 15H]TJO[ RVFP[ RVFSIPKNL RUIQKNL",
	2752: " 42H]OJPKOLNKNJOHPGSFVFYGZIZKYMWOTQPSMUKWI[ RVFXGYIYKXMVOPS RJYKXMXRZUZWYXW RMXR[U[WZXW",
	2753: " 50H]OJPKOLNKNJOHPGSFVFYGZIZKYMVOSP RVFXGYIYKXMVO RQPSPVQWRXTXWWYVZS[O[LZKYJWJVKULVKW RSPUQVRWTWWVYUZS[",
	2754: " 10H]XGR[ RYFS[ RYFJUZU",
	2755: " 39H]QFLP RQF[F RQGVG[F RLPMOPNSNVOWPXRXUWXUZR[O[LZKYJWJVKULVKW RSNUOVPWRWUVXTZR[",
	2756: " 46H]YIXJYKZJZIYGWFTFQGOIMLLOKSKWLYMZO[R[UZWXXVXSWQVPTOQOOPMRLT RTFRGPINLMOLSLXMZ RR[TZVXWVWRVP",
	2757: " 30H]NFLL R[FZIXLSRQUPWO[ RXLRRPUOWN[ RMIPFRFWI RNHPGRGWIYIZH[F",
	2758: " 63H]SFPGOHNJNMOOQPTPXOYNZLZIYGVFSF RSFQGPHOJOMPOQP RTPWOXNYLYIXGVF RQPMQKSJUJXKZN[R[VZWYXWXTWRVQTP RQPNQLSKUKXLZN[ RR[UZVYWWWSVQ",
	2759: " 46H]YMXOVQTRQROQNPMNMKNIPGSFVFXGYHZJZNYRXUVXTZQ[N[LZKXKWLVMWLX ROQNONKOIQGSF RXGYIYNXRWUUXSZQ[",
	2760: "  6MXPYOZP[QZPY",
	2761: "  8MXP[OZPYQZQ[P]N_",
	2762: " 11MXSMRNSOTNSM RPYOZP[QZ",
	2763: " 14MXSMRNSOTNSM RP[OZPYQZQ[P]N_",
	2764: " 17MXUFTGRS RUGRS RUFVGRS RPYOZP[QZPY",
	2765: " 34H]OJPKOLNKNJOHPGSFWFZG[I[KZMYNSPQQQSRTTT RWFYGZIZKYMXNVO RPYOZP[QZPY",
	2766: "  8MXVFTHSJSKTLUKTJ",
	2767: "  8MXUHTGUFVGVHUJSL",
	2768: " 55E_\\N[O\\P]O]N\\M[MYNWPRXPZN[K[HZGXGVHTISKRPPROTMUKUITGRFPGOIOLPRQUSXUZW[Y[ZYZX RK[IZHXHVITJSPP ROLPQQTSWUYWZYZZY",
	2769: " 41H]TBL_ RYBQ_ RZJYKZL[K[JZHYGVFRFOGMIMKNMONVRXT RMKOMVQWRXTXWWYVZS[O[LZKYJWJVKULVKW",
	2770: "  3G]_BEb",
	2771: " 20KZZBVESHQKOONTNXO]P`Qb RVESIQMPPOUOZP_Qb",
	2772: " 20JYSBTDUGVLVPUUSYQ\\N_Jb RSBTEUJUOTTSWQ[N_",
	2773: "  9J[TFTR ROIYO RYIOO",
	2774: "  3E_IR[R",
	2775: "  6E_RIR[ RIR[R",
	2776: "  6E_IO[O RIU[U",
	2777: "  6NWUFSM RVFSM",
	2778: " 12I[PFNM RQFNM RYFWM RZFWM",
	2779: " 14KZSFQGPIPKQMSNUNWMXKXIWGUFSF",
	2801: " 18H\\RFK[ RRFY[ RRIX[ RMUVU RI[O[ RU[[[",
	2802: " 31G]LFL[ RMFM[ RIFYFYLXF RMPUPXQYRZTZWYYXZU[I[ RUPWQXRYTYWXYWZU[",
	2803: " 45G]LFL[ RMFM[ RIFUFXGYHZJZLYNXOUP RUFWGXHYJYLXNWOUP RMPUPXQYRZTZWYYXZU[I[ RUPWQXRYTYWXYWZU[",
	2804: " 14I[NFN[ ROFO[ RKFZFZLYF RK[R[",
	2805: " 31F^NFNLMTLXKZJ[ RXFX[ RYFY[ RKF\\F RG[\\[ RG[Gb RH[Gb R[[\\b R\\[\\b",
	2806: " 22G\\LFL[ RMFM[ RSLST RIFYFYLXF RMPSP RI[Y[YUX[",
	2807: " 71CbRFR[ RSFS[ ROFVF RGGHHGIFHFGGFHFIGJIKMLONPWPYOZM[I\\G]F^F_G_H^I]H^G RNPLQKSJXIZH[ RNPMQLSKXJZI[G[FZEX RWPYQZS[X\\Z][ RWPXQYSZX[Z\\[^[_Z`X RO[V[",
	2808: " 45H\\LIKFKLLINGPFTFWGXIXLWNTOQO RTFVGWIWLVNTO RTOVPXRYTYWXYWZT[O[MZLYKWKVLUMVLW RWQXTXWWYVZT[",
	2809: " 27F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\\F RXHLY RH[O[ RU[\\[",
	2810: " 37F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\\F RXHLY RH[O[ RU[\\[ RN@N?M?M@NBPCTCVBW@",
	2811: " 43F^KFK[ RLFL[ RHFOF RLPSPUOVMWIXGYFZF[G[HZIYHZG RSPUQVSWXXZY[ RSPTQUSVXWZX[Z[[Z\\X RH[O[",
	2812: " 25E^MFMLLTKXJZI[H[GZGYHXIYHZ RXFX[ RYFY[ RJF\\F RU[\\[",
	2813: " 30F_KFK[ RLFRX RKFR[ RYFR[ RYFY[ RZFZ[ RHFLF RYF]F RH[N[ RV[][",
	2814: " 27F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\\F RLPXP RH[O[ RU[\\[",
	2815: " 44G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF",
	2816: " 21F^KFK[ RLFL[ RXFX[ RYFY[ RHF\\F RH[O[ RU[\\[",
	2817: " 29G]LFL[ RMFM[ RIFUFXGYHZJZMYOXPUQMQ RUFWGXHYJYMXOWPUQ RI[P[",
	2818: " 32G\\XIYLYFXIVGSFQFNGLIKKJNJSKVLXNZQ[S[VZXXYV RQFOGMILKKNKSLVMXOZQ[",
	2819: " 16I\\RFR[ RSFS[ RLFKLKFZFZLYF RO[V[",
	2820: " 24H]KFRV RLFSV RZFSVQYPZN[M[LZLYMXNYMZ RIFOF RVF\\F",
	2821: " 48F_RFR[ RSFS[ ROFVF RPILJJLIOIRJULWPXUXYW[U\\R\\O[LYJUIPI RPIMJKLJOJRKUMWPX RUXXWZU[R[OZLXJUI RO[V[",
	2822: " 21H\\KFX[ RLFY[ RYFK[ RIFOF RUF[F RI[O[ RU[[[",
	2823: " 27F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\\F RH[\\[ R[[\\b R\\[\\b",
	2824: " 28F]KFKQLSOTRTUSWQ RLFLQMSOT RWFW[ RXFX[ RHFOF RTF[F RT[[[",
	2825: " 30BcGFG[ RHFH[ RRFR[ RSFS[ R]F][ R^F^[ RDFKF ROFVF RZFaF RD[a[",
	2826: " 36BcGFG[ RHFH[ RRFR[ RSFS[ R]F][ R^F^[ RDFKF ROFVF RZFaF RD[a[ R`[ab Ra[ab",
	2827: " 31F`PFP[ RQFQ[ RIFHLHFTF RQPXP[Q\\R]T]W\\Y[ZX[M[ RXPZQ[R\\T\\W[YZZX[",
	2828: " 41CaHFH[ RIFI[ REFLF RIPPPSQTRUTUWTYSZP[E[ RPPRQSRTTTWSYRZP[ R[F[[ R\\F\\[ RXF_F RX[_[",
	2829: " 29H]MFM[ RNFN[ RJFQF RNPUPXQYRZTZWYYXZU[J[ RUPWQXRYTYWXYWZU[",
	2830: " 39H]LIKFKLLINGQFSFVGXIYKZNZSYVXXVZS[P[MZLYKWKVLUMVLW RSFUGWIXKYNYSXVWXUZS[ RPPYP",
	2831: " 59CbHFH[ RIFI[ REFLF RE[L[ RVFSGQIPKOOORPVQXSZV[X[[Z]X^V_R_O^K]I[GXFVF RVFTGRIQKPOPRQVRXTZV[ RX[ZZ\\X]V^R^O]K\\IZGXF RIPOP",
	2832: " 45G]WFW[ RXFX[ R[FOFLGKHJJJLKNLOOPWP ROFMGLHKJKLLNMOOP RRPPQORLYKZJZIY RPQOSMZL[J[IYIX RT[[[",
	2901: " 39I]NONPMPMONNPMTMVNWOXQXXYZZ[ RWOWXXZZ[[[ RWQVRPSMTLVLXMZP[S[UZWX RPSNTMVMXNZP[",
	2902: " 48H\\XFWGQINKLNKQKULXNZQ[S[VZXXYUYSXPVNSMQMNNLPKS RXFWHUIQJNLLN RQMONMPLSLUMXOZQ[ RS[UZWXXUXSWPUNSM",
	2903: " 37H\\MMM[ RNMN[ RJMUMXNYPYQXSUT RUMWNXPXQWSUT RNTUTXUYWYXXZU[J[ RUTWUXWXXWZU[",
	2904: " 14HZMMM[ RNMN[ RJMXMXRWM RJ[Q[",
	2905: " 22F]NMNQMWLZK[ RWMW[ RXMX[ RKM[M RI[H`H[[[[`Z[",
	2906: " 31H[LSXSXQWOVNTMQMNNLPKSKULXNZQ[S[VZXX RWSWPVN RQMONMPLSLUMXOZQ[",
	2907: " 59E`RMR[ RSMS[ ROMVM RJNIOHNIMJMKNMRNSPTUTWSXRZN[M\\M]N\\O[N RPTNUMVKZJ[ RPTNVLZK[I[HZGX RUTWUXVZZ[[ RUTWVYZZ[\\[]Z^X RO[V[",
	2908: " 42I[MOLMLQMONNPMTMWNXPXQWSTT RTMVNWPWQVSTT RQTTTWUXWXXWZT[P[MZLXLWMVNWMX RTTVUWWWXVZT[",
	2909: " 27G]LML[ RMMM[ RWMW[ RXMX[ RIMPM RTM[M RI[P[ RT[[[ RWNMZ",
	2910: " 37G]LML[ RMMM[ RWMW[ RXMX[ RIMPM RTM[M RI[P[ RT[[[ RWNMZ ROGOFNFNGOIQJSJUIVG",
	2911: " 38H\\MMM[ RNMN[ RJMQM RNTPTSSTRVNWMXMYNXOWN RPTSUTVVZW[ RPTRUSVUZV[X[YZZX RJ[Q[",
	2912: " 22G]NMNQMWLZK[J[IZJYKZ RWMW[ RXMX[ RKM[M RT[[[",
	2913: " 30G^LML[ RLMR[ RMMRY RXMR[ RXMX[ RYMY[ RIMMM RXM\\M RI[O[ RU[\\[",
	2914: " 27G]LML[ RMMM[ RWMW[ RXMX[ RIMPM RTM[M RMTWT RI[P[ RT[[[",
	2915: " 36H\\QMNNLPKSKULXNZQ[S[VZXXYUYSXPVNSMQM RQMONMPLSLUMXOZQ[ RS[UZWXXUXSWPUNSM",
	2916: " 21G]LML[ RMMM[ RWMW[ RXMX[ RIM[M RI[P[ RT[[[",
	2917: " 36G\\LMLb RMMMb RMPONQMSMVNXPYSYUXXVZS[Q[OZMX RSMUNWPXSXUWXUZS[ RIMMM RIbPb",
	2918: " 28H[WPVQWRXQXPVNTMQMNNLPKSKULXNZQ[S[VZXX RQMONMPLSLUMXOZQ[",
	2919: " 16I\\RMR[ RSMS[ RMMLRLMYMYRXM RO[V[",
	2920: " 22I[LMR[ RMMRY RXMR[P_NaLbKbJaK`La RJMPM RTMZM",
	2921: " 52H]RFRb RSFSb ROFSF RRPQNPMNMLNKQKWLZN[P[QZRX RNMMNLQLWMZN[ RWMXNYQYWXZW[ RSPTNUMWMYNZQZWYZW[U[TZSX RObVb",
	2922: " 21H\\LMW[ RMMX[ RXML[ RJMPM RTMZM RJ[P[ RT[Z[",
	2923: " 23G]LML[ RMMM[ RWMW[ RXMX[ RIMPM RTM[M RI[[[[`Z[",
	2924: " 28G]LMLTMVPWRWUVWT RMMMTNVPW RWMW[ RXMX[ RIMPM RTM[M RT[[[",
	2925: " 30CbHMH[ RIMI[ RRMR[ RSMS[ R\\M\\[ R]M][ REMLM ROMVM RYM`M RE[`[",
	2926: " 32CbHMH[ RIMI[ RRMR[ RSMS[ R\\M\\[ R]M][ REMLM ROMVM RYM`M RE[`[``_[",
	2927: " 27H]QMQ[ RRMR[ RLMKRKMUM RRTVTYUZWZXYZV[N[ RVTXUYWYXXZV[",
	2928: " 37E_JMJ[ RKMK[ RGMNM RKTOTRUSWSXRZO[G[ ROTQURWRXQZO[ RYMY[ RZMZ[ RVM]M RV[][",
	2929: " 25J[OMO[ RPMP[ RLMSM RPTTTWUXWXXWZT[L[ RTTVUWWWXVZT[",
	2930: " 34I\\MOLMLQMONNPMSMVNXPYSYUXXVZS[P[NZLXLWMVNWMX RSMUNWPXSXUWXUZS[ RRTXT",
	2931: " 51DaIMI[ RJMJ[ RFMMM RF[M[ RVMSNQPPSPUQXSZV[X[[Z]X^U^S]P[NXMVM RVMTNRPQSQURXTZV[ RX[ZZ\\X]U]S\\PZNXM RJTPT",
	2932: " 40G\\VMV[ RWMW[ RZMOMLNKPKQLSOTVT ROMMNLPLQMSOT RTTQUPVNZM[ RTTRUQVOZN[L[KZJX RS[Z[",
	3001: " 36H\\RFKZ RQIW[ RRIX[ RRFY[ RMUVU RI[O[ RT[[[ RKZJ[ RKZM[ RWZU[ RWYV[ RXYZ[",
	3002: " 78G]LFL[ RMGMZ RNFN[ RIFUFXGYHZJZLYNXOUP RXHYJYLXN RUFWGXIXMWOUP RNPUPXQYRZTZWYYXZU[I[ RXRYTYWXY RUPWQXSXXWZU[ RJFLG RKFLH ROFNH RPFNG RLZJ[ RLYK[ RNYO[ RNZP[",
	3003: " 37G\\XIYFYLXIVGTFQFNGLIKKJNJSKVLXNZQ[T[VZXXYV RMILKKNKSLVMX RQFOGMJLNLSMWOZQ[",
	3004: " 62G]LFL[ RMGMZ RNFN[ RIFSFVGXIYKZNZSYVXXVZS[I[ RWIXKYNYSXVWX RSFUGWJXNXSWWUZS[ RJFLG RKFLH ROFNH RPFNG RLZJ[ RLYK[ RNYO[ RNZP[",
	3005: " 83G\\LFL[ RMGMZ RNFN[ RIFYFYL RNPTP RTLTT RI[Y[YU RJFLG RKFLH ROFNH RPFNG RTFYG RVFYH RWFYI RXFYL RTLSPTT RTNRPTR RTOPPTQ RLZJ[ RLYK[ RNYO[ RNZP[ RT[YZ RV[YY RW[YX RX[YU",
	3006: " 70G[LFL[ RMGMZ RNFN[ RIFYFYL RNPTP RTLTT RI[Q[ RJFLG RKFLH ROFNH RPFNG RTFYG RVFYH RWFYI RXFYL RTLSPTT RTNRPTR RTOPPTQ RLZJ[ RLYK[ RNYO[ RNZP[",
	3007: " 60G^XIYFYLXIVGTFQFNGLIKKJNJSKVLXNZQ[T[VZXZY[YS RMILKKNKSLVMX RQFOGMJLNLSMWOZQ[ RXTXY RWSWYVZ RTS\\S RUSWT RVSWU RZSYU R[SYT",
	3008: " 81F^KFK[ RLGLZ RMFM[ RWFW[ RXGXZ RYFY[ RHFPF RTF\\F RMPWP RH[P[ RT[\\[ RIFKG RJFKH RNFMH ROFMG RUFWG RVFWH RZFYH R[FYG RKZI[ RKYJ[ RMYN[ RMZO[ RWZU[ RWYV[ RYYZ[ RYZ[[",
	3009: " 39LXQFQ[ RRGRZ RSFS[ RNFVF RN[V[ ROFQG RPFQH RTFSH RUFSG RQZO[ RQYP[ RSYT[ RSZU[",
	3010: " 45JYSFSWRZQ[ RTGTWSZ RUFUWTZQ[O[MZLXLVMUNUOVOWNXMX RMVMWNWNVMV RPFXF RQFSG RRFSH RVFUH RWFUG",
	3011: " 69F\\KFK[ RLGLZ RMFM[ RXGMR RPPW[ RQPX[ RQNY[ RHFPF RUF[F RH[P[ RT[[[ RIFKG RJFKH RNFMH ROFMG RWFXG RZFXG RKZI[ RKYJ[ RMYN[ RMZO[ RWYU[ RWYZ[",
	3012: " 52I[NFN[ ROGOZ RPFP[ RKFSF RK[Z[ZU RLFNG RMFNH RQFPH RRFPG RNZL[ RNYM[ RPYQ[ RPZR[ RU[ZZ RW[ZY RX[ZX RY[ZU",
	3013: " 63E_JFJZ RJFQ[ RKFQX RLFRX RXFQ[ RXFX[ RYGYZ RZFZ[ RGFLF RXF]F RG[M[ RU[][ RHFJG R[FZH R\\FZG RJZH[ RJZL[ RXZV[ RXYW[ RZY[[ RZZ\\[",
	3014: " 39F^KFKZ RKFY[ RLFXX RMFYX RYGY[ RHFMF RVF\\F RH[N[ RIFKG RWFYG R[FYG RKZI[ RKZM[",
	3015: " 54G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RMILKKNKSLVMX RWXXVYSYNXKWI RQFOGMJLNLSMWOZQ[ RS[UZWWXSXNWJUGSF",
	3016: " 59G]LFL[ RMGMZ RNFN[ RIFUFXGYHZJZMYOXPUQNQ RXHYJYMXO RUFWGXIXNWPUQ RI[Q[ RJFLG RKFLH ROFNH RPFNG RLZJ[ RLYK[ RNYO[ RNZP[",
	3017: " 77G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RMILKKNKSLVMX RWXXVYSYNXKWI RQFOGMJLNLSMWOZQ[ RS[UZWWXSXNWJUGSF RNXOVQURUTVUXV^W`Y`Z^Z\\ RV\\W^X_Y_ RUXW]X^Y^Z]",
	3018: " 80G]LFL[ RMGMZ RNFN[ RIFUFXGYHZJZLYNXOUPNP RXHYJYLXN RUFWGXIXMWOUP RRPTQUSWYX[Z[[Y[W RWWXYYZZZ RTQURXXYYZY[X RI[Q[ RJFLG RKFLH ROFNH RPFNG RLZJ[ RLYK[ RNYO[ RNZP[",
	3019: " 44H\\XIYFYLXIVGSFPFMGKIKLLNOPURWSXUXXWZ RLLMNOOUQWRXT RMGLILKMMONUPXRYTYWXYWZT[Q[NZLXKUK[LX",
	3020: " 57H\\JFJL RQFQ[ RRGRZ RSFS[ RZFZL RJFZF RN[V[ RKFJL RLFJI RMFJH ROFJG RUFZG RWFZH RXFZI RYFZL RQZO[ RQYP[ RSYT[ RSZU[",
	3021: " 45F^KFKULXNZQ[S[VZXXYUYG RLGLVMX RMFMVNYOZQ[ RHFPF RVF\\F RIFKG RJFKH RNFMH ROFMG RWFYG R[FYG",
	3022: " 34H\\KFR[ RLFRXR[ RMFSX RYGR[ RIFPF RUF[F RJFLH RNFMH ROFMG RWFYG RZFYG",
	3023: " 55F^JFN[ RKFNVN[ RLFOV RRFOVN[ RRFV[ RSFVVV[ RTFWV RZGWVV[ RGFOF RRFTF RWF]F RHFKG RIFKH RMFLH RNFLG RXFZG R\\FZG",
	3024: " 54H\\KFW[ RLFX[ RMFY[ RXGLZ RIFPF RUF[F RI[O[ RT[[[ RJFMH RNFMH ROFMG RVFXG RZFXG RLZJ[ RLZN[ RWZU[ RWYV[ RWYZ[",
	3025: " 48G]JFQQQ[ RKFRQRZ RLFSQS[ RYGSQ RHFOF RVF\\F RN[V[ RIFKG RNFLG RWFYG R[FYG RQZO[ RQYP[ RSYT[ RSZU[",
	3026: " 41H\\YFKFKL RWFK[ RXFL[ RYFM[ RK[Y[YU RLFKL RMFKI RNFKH RPFKG RT[YZ RV[YY RW[YX RX[YU",
	3051: " 38H\\UFIZ RSJT[ RTHUZ RUFUHVYV[ RLUTU RF[L[ RQ[X[ RIZG[ RIZK[ RTZR[ RTYS[ RVYW[",
	3052: " 78F^OFI[ RPFJ[ RQFK[ RLFWFZG[I[KZNYOVP RYGZIZKYNXO RWFXGYIYKXNVP RNPVPXQYSYUXXVZR[F[ RWQXSXUWXUZ RVPWRWUVXTZR[ RMFPG RNFOH RRFPH RSFPG RJZG[ RJYH[ RKYL[ RJZM[",
	3053: " 41H]ZH[H\\F[L[JZHYGWFTFQGOIMLLOKSKVLYMZP[S[UZWXXV RQHOJNLMOLSLWMY RTFRGPJOLNOMSMXNZP[",
	3054: " 63F]OFI[ RPFJ[ RQFK[ RLFUFXGYHZKZOYSWWUYSZO[F[ RWGXHYKYOXSVWTY RUFWHXKXOWSUWRZO[ RMFPG RNFOH RRFPH RSFPG RJZG[ RJYH[ RKYL[ RJZM[",
	3055: " 80F]OFI[ RPFJ[ RQFK[ RULST RLF[FZL RNPTP RF[U[WV RMFPG RNFOH RRFPH RSFPG RWFZG RXFZH RYFZI RZFZL RULSPST RTNRPSR RTOQPSQ RJZG[ RJYH[ RKYL[ RJZM[ RP[UZ RR[UY RUYWV",
	3056: " 70F\\OFI[ RPFJ[ RQFK[ RULST RLF[FZL RNPTP RF[N[ RMFPG RNFOH RRFPH RSFPG RWFZG RXFZH RYFZI RZFZL RULSPST RTNRPSR RTOQPSQ RJZG[ RJYH[ RKYL[ RJZM[",
	3057: " 65H^ZH[H\\F[L[JZHYGWFTFQGOIMLLOKSKVLYMZP[R[UZWXYT RQHOJNLMOLSLWMY RVXWWXT RTFRGPJOLNOMSMXNZP[ RR[TZVWWT RTT\\T RUTWU RVTWW RZTXV R[TXU",
	3058: " 81E_NFH[ ROFI[ RPFJ[ RZFT[ R[FU[ R\\FV[ RKFSF RWF_F RLPXP RE[M[ RQ[Y[ RLFOG RMFNH RQFOH RRFOG RXF[G RYFZH R]F[H R^F[G RIZF[ RIYG[ RJYK[ RIZL[ RUZR[ RUYS[ RVYW[ RUZX[",
	3059: " 39KYTFN[ RUFO[ RVFP[ RQFYF RK[S[ RRFUG RSFTH RWFUH RXFUG ROZL[ ROYM[ RPYQ[ ROZR[",
	3060: " 47I\\WFRWQYO[ RXFTSSVRX RYFUSSXQZO[M[KZJXJVKULUMVMWLXKX RKVKWLWLVKV RTF\\F RUFXG RVFWH RZFXH R[FXG",
	3061: " 72F]OFI[ RPFJ[ RQFK[ R\\GMR RQOU[ RROV[ RSNWZ RLFTF RYF_F RF[N[ RR[Y[ RMFPG RNFOH RRFPH RSFPG RZF\\G R^F\\G RJZG[ RJYH[ RKYL[ RJZM[ RUZS[ RUYT[ RVYX[",
	3062: " 49H\\QFK[ RRFL[ RSFM[ RNFVF RH[W[YU ROFRG RPFQH RTFRH RUFRG RLZI[ RLYJ[ RMYN[ RLZO[ RR[WZ RT[XX RV[YU",
	3063: " 68D`MFGZ RMGNYN[ RNFOY ROFPX R[FPXN[ R[FU[ R\\FV[ R]FW[ RJFOF R[F`F RD[J[ RR[Z[ RKFMG RLFMH R^F\\H R_F\\G RGZE[ RGZI[ RVZS[ RVYT[ RWYX[ RVZY[",
	3064: " 43F_OFIZ ROFV[ RPFVX RQFWX R\\GWXV[ RLFQF RYF_F RF[L[ RMFPG RNFPH RZF\\G R^F\\G RIZG[ RIZK[",
	3065: " 56G]SFPGNILLKOJSJVKYLZN[Q[TZVXXUYRZNZKYHXGVFSF ROIMLLOKSKWLY RUXWUXRYNYJXH RSFQGOJNLMOLSLXMZN[ RQ[SZUWVUWRXNXIWGVF",
	3066: " 60F]OFI[ RPFJ[ RQFK[ RLFXF[G\\I\\K[NYPUQMQ RZG[I[KZNXP RXFYGZIZKYNWPUQ RF[N[ RMFPG RNFOH RRFPH RSFPG RJZG[ RJYH[ RKYL[ RJZM[",
	3067: " 78G]SFPGNILLKOJSJVKYLZN[Q[TZVXXUYRZNZKYHXGVFSF ROIMLLOKSKWLY RUXWUXRYNYJXH RSFQGOJNLMOLSLXMZN[ RQ[SZUWVUWRXNXIWGVF RLXMVOUPURVSXT]U^V^W] RT^U_V_ RSXS_T`V`W]W\\",
	3068: " 78F^OFI[ RPFJ[ RQFK[ RLFWFZG[I[KZNYOVPNP RYGZIZKYNXO RWFXGYIYKXNVP RRPTQURWXXYYYZX RWYXZYZ RURVZW[Y[ZXZW RF[N[ RMFPG RNFOH RRFPH RSFPG RJZG[ RJYH[ RKYL[ RJZM[",
	3069: " 44G^ZH[H\\F[L[JZHYGVFRFOGMIMLNNPPVSWUWXVZ RNLONVRWT ROGNINKOMUPWRXTXWWYVZS[O[LZKYJWJUI[JYKY",
	3070: " 54G]TFN[ RUFO[ RVFP[ RMFKL R]F\\L RMF]F RK[S[ RNFKL RPFLI RRFMG RYF\\G RZF\\H R[F\\I R\\F\\L ROZL[ ROYM[ RPYQ[ ROZR[",
	3071: " 48F_NFKQJUJXKZN[R[UZWXXU\\G ROFLQKUKYLZ RPFMQLULYN[ RKFSF RYF_F RLFOG RMFNH RQFOH RRFOG RZF\\G R^F\\G",
	3072: " 35H\\NFNHOYO[ ROGPX RPFQW R[GO[ RLFSF RXF^F RMFNH RQFPH RRFOG RYF[G R]F[G",
	3073: " 57E_MFMHKYK[ RNGLX ROFMW RUFMWK[ RUFUHSYS[ RVGTX RWFUW R]GUWS[ RJFRF RUFWF RZF`F RKFNG RLFMH RPFNI RQFNG R[F]G R_F]G",
	3074: " 54G]NFT[ ROFU[ RPFV[ R[GIZ RLFSF RXF^F RF[L[ RQ[X[ RMFOH RQFPH RRFPG RYF[G R]F[G RIZG[ RIZK[ RTZR[ RTYS[ RUYW[",
	3075: " 51G]MFQPN[ RNFRPO[ ROFSPP[ R\\GSP RKFRF RYF_F RK[S[ RLFNG RPFOH RQFNG RZF\\G R^F\\G ROZL[ ROYM[ RPYQ[ ROZR[",
	3076: " 35G]ZFH[ R[FI[ R\\FJ[ R\\FNFLL RH[V[XU ROFLL RPFMI RRFNG RR[VZ RT[WX RU[XU",
	3101: " 54I]NPNOOOOQMQMONNPMTMVNWOXQXXYZZ[ RVOWQWXXZ RTMUNVPVXWZZ[[[ RVRUSPTMULWLXMZP[S[UZVX RNUMWMXNZ RUSQTOUNWNXOZP[",
	3102: " 47G\\LFL[MZOZ RMGMY RIFNFNZ RNPONQMSMVNXPYSYUXXVZS[Q[OZNX RWPXRXVWX RSMUNVOWRWVVYUZS[ RJFLG RKFLH",
	3103: " 34H[WQWPVPVRXRXPVNTMQMNNLPKSKULXNZQ[S[VZXX RMPLRLVMX RQMONNOMRMVNYOZQ[",
	3104: " 52H]VFV[[[ RWGWZ RSFXFX[ RVPUNSMQMNNLPKSKULXNZQ[S[UZVX RMPLRLVMX RQMONNOMRMVNYOZQ[ RTFVG RUFVH RXYY[ RXZZ[",
	3105: " 41H[MSXSXQWOVNSMQMNNLPKSKULXNZQ[S[VZXX RWRWQVO RMPLRLVMX RVSVPUNSM RQMONNOMRMVNYOZQ[",
	3106: " 40KYWHWGVGVIXIXGWFTFRGQHPKP[ RRHQKQZ RTFSGRIR[ RMMVM RM[U[ RPZN[ RPYO[ RRYS[ RRZT[",
	3107: " 89I\\XNYOZNYMXMVNUO RQMONNOMQMSNUOVQWSWUVVUWSWQVOUNSMQM ROONQNSOU RUUVSVQUO RQMPNOPOTPVQW RSWTVUTUPTNSM RNUMVLXLYM[N\\Q]U]X^Y_ RN[Q\\U\\X] RLYMZP[U[X\\Y^Y_XaUbObLaK_K^L\\O[ RObMaL_L^M\\O[",
	3108: " 65G^LFL[ RMGMZ RIFNFN[ RNQOOPNRMUMWNXOYRY[ RWOXRXZ RUMVNWQW[ RI[Q[ RT[\\[ RJFLG RKFLH RLZJ[ RLYK[ RNYO[ RNZP[ RWZU[ RWYV[ RYYZ[ RYZ[[",
	3109: " 43LXQFQHSHSFQF RRFRH RQGSG RQMQ[ RRNRZ RNMSMS[ RN[V[ ROMQN RPMQO RQZO[ RQYP[ RSYT[ RSZU[",
	3110: " 41KXRFRHTHTFRF RSFSH RRGTG RRMR^QaPb RSNS]R` ROMTMT]S`RaPbMbLaL_N_NaMaM` RPMRN RQMRO",
	3111: " 61G]LFL[ RMGMZ RIFNFN[ RWNNW RRSY[ RRTX[ RQTW[ RTM[M RI[Q[ RT[[[ RJFLG RKFLH RUMWN RZMWN RLZJ[ RLYK[ RNYO[ RNZP[ RWYU[ RVYZ[",
	3112: " 31LXQFQ[ RRGRZ RNFSFS[ RN[V[ ROFQG RPFQH RQZO[ RQYP[ RSYT[ RSZU[",
	3113: " 99AcFMF[ RGNGZ RCMHMH[ RHQIOJNLMOMQNROSRS[ RQORRRZ ROMPNQQQ[ RSQTOUNWMZM\\N]O^R^[ R\\O]R]Z RZM[N\\Q\\[ RC[K[ RN[V[ RY[a[ RDMFN REMFO RFZD[ RFYE[ RHYI[ RHZJ[ RQZO[ RQYP[ RSYT[ RSZU[ R\\ZZ[ R\\Y[[ R^Y_[ R^Z`[",
	3114: " 65G^LML[ RMNMZ RIMNMN[ RNQOOPNRMUMWNXOYRY[ RWOXRXZ RUMVNWQW[ RI[Q[ RT[\\[ RJMLN RKMLO RLZJ[ RLYK[ RNYO[ RNZP[ RWZU[ RWYV[ RYYZ[ RYZ[[",
	3115: " 46H\\QMNNLPKSKULXNZQ[S[VZXXYUYSXPVNSMQM RMPLRLVMX RWXXVXRWP RQMONNOMRMVNYOZQ[ RS[UZVYWVWRVOUNSM",
	3116: " 60G\\LMLb RMNMa RIMNMNb RNPONQMSMVNXPYSYUXXVZS[Q[OZNX RWPXRXVWX RSMUNVOWRWVVYUZS[ RIbQb RJMLN RKMLO RLaJb RL`Kb RN`Ob RNaPb",
	3117: " 55H\\VNVb RWOWa RUNWNXMXb RVPUNSMQMNNLPKSKULXNZQ[S[UZVX RMPLRLVMX RQMONNOMRMVNYOZQ[ RSb[b RVaTb RV`Ub RX`Yb RXaZb",
	3118: " 43IZNMN[ RONOZ RKMPMP[ RWOWNVNVPXPXNWMUMSNQPPS RK[S[ RLMNN RMMNO RNZL[ RNYM[ RPYQ[ RPZR[",
	3119: " 43J[WOXMXQWOVNTMPMNNMOMQNSPTUUWVXY RNNMQ RNRPSUTWU RXVWZ RMONQPRUSWTXVXYWZU[Q[OZNYMWM[NY",
	3120: " 22KZPHPVQYRZT[V[XZYX RQHQWRY RPHRFRWSZT[ RMMVM",
	3121: " 43G^LMLVMYNZP[S[UZVYWW RMNMWNY RIMNMNWOZP[ RWMW[\\[ RXNXZ RTMYMY[ RJMLN RKMLO RYYZ[ RYZ[[",
	3122: " 31I[LMR[ RMMRY RNMSY RXNSYR[ RJMQM RTMZM RKMNO RPMNN RVMXN RYMXN",
	3123: " 45F^JMN[ RKMNX RLMOX RRMOXN[ RRMV[ RSMVX RRMTMWX RZNWXV[ RGMOM RWM]M RHMKN RNMLN RXMZN R\\MZN",
	3124: " 48H\\LMV[ RMMW[ RNMX[ RWNMZ RJMQM RTMZM RJ[P[ RS[Z[ RKMMN RPMNN RUMWN RYMWN RMZK[ RMZO[ RVZT[ RWZY[",
	3125: " 40H[LMR[ RMMRY RNMSY RXNSYP_NaLbJbIaI_K_KaJaJ` RJMQM RTMZM RKMNO RPMNN RVMXN RYMXN",
	3126: " 41I[VML[ RWMM[ RXMN[ RXMLMLQ RL[X[XW RMMLQ RNMLP ROMLO RQMLN RS[XZ RU[XY RV[XX RW[XW",
	3151: " 50G]WMUTUXVZW[Y[[Y\\W RXMVTVZ RWMYMWTVX RUTUQTNRMPMMNKQJTJVKYLZN[P[RZSYTWUT RNNLQKTKWLY RPMNOMQLTLWMZN[",
	3152: " 52I\\PFNMMSMWNYOZQ[S[VZXWYTYRXOWNUMSMQNPOOQNT RQFOMNQNWOZ RVYWWXTXQWO RMFRFPMNT RS[UYVWWTWQVNUM RNFQG ROFPH",
	3153: " 34I[WQWPVPVRXRXPWNUMRMONMQLTLVMYNZP[R[UZWW ROONQMTMWNY RRMPOOQNTNWOZP[",
	3154: " 58G]YFVQUUUXVZW[Y[[Y\\W RZFWQVUVZ RVF[FWTVX RUTUQTNRMPMMNKQJTJVKYLZN[P[RZSYTWUT RMOLQKTKWLY RPMNOMQLTLWMZN[ RWFZG RXFYH",
	3155: " 33I[MVQUTTWRXPWNUMRMONMQLTLVMYNZP[R[UZWX ROONQMTMWNY RRMPOOQNTNWOZP[",
	3156: " 45JZZHZGYGYI[I[GZFXFVGTISKRNQRO[N^M`Kb RTJSMRRP[O^ RXFVHUJTMSRQZP]O_MaKbIbHaH_J_JaIaI` RNMYM",
	3157: " 57H]XMT[S^QaOb RYMU[S_ RXMZMV[T_RaObLbJaI`I^K^K`J`J_ RVTVQUNSMQMNNLQKTKVLYMZO[Q[SZTYUWVT RNOMQLTLWMY RQMOONQMTMWNZO[",
	3158: " 41G]OFI[K[ RPFJ[ RLFQFK[ RMTOPQNSMUMWNXPXSVX RWNWRVVVZ RWPUUUXVZW[Y[[Y\\W RMFPG RNFOH",
	3159: " 35KXSFSHUHUFSF RTFTH RSGUG RLQMOOMQMRNSPSSQX RRNRRQVQZ RRPPUPXQZR[T[VYWW",
	3160: " 45KXUFUHWHWFUF RVFVH RUGWG RMQNOPMRMSNTPTSRZQ]P_NaLbJbIaI_K_KaJaJ` RSNSSQZP]O_ RSPRTP[O^N`Lb",
	3161: " 49G]OFI[K[ RPFJ[ RLFQFK[ RYOYNXNXPZPZNYMWMUNQROS RMSOSQTRUTYUZWZ RQUSYTZ ROSPTRZS[U[WZYW RMFPG RNFOH",
	3162: " 26LXTFQQPUPXQZR[T[VYWW RUFRQQUQZ RQFVFRTQX RRFUG RSFTH",
	3163: " 61@cAQBODMFMGNHPHSF[ RGNGSE[ RGPFTD[F[ RHSJPLNNMPMRNSPSSQ[ RRNRSP[ RRPQTO[Q[ RSSUPWNYM[M]N^P^S\\X R]N]R\\V\\Z R]P[U[X\\Z][_[aYbW",
	3164: " 42F^GQHOJMLMMNNPNSL[ RMNMSK[ RMPLTJ[L[ RNSPPRNTMVMXNYPYSWX RXNXRWVWZ RXPVUVXWZX[Z[\\Y]W",
	3165: " 46H\\QMNNLQKTKVLYMZP[S[VZXWYTYRXOWNTMQM RNOMQLTLWMY RVYWWXTXQWO RQMOONQMTMWNZP[ RS[UYVWWTWQVNTM",
	3166: " 66G]HQIOKMMMNNOPOSNWKb RNNNSMWJb RNPMTIb ROTPQQORNTMVMXNYOZRZTYWWZT[R[PZOWOT RXOYQYTXWWY RVMWNXQXTWWVYT[ RFbNb RJaGb RJ`Hb RK`Lb RJaMb",
	3167: " 57G\\WMQb RXMRb RWMYMSb RUTUQTNRMPMMNKQJTJVKYLZN[P[RZSYTWUT RMOLQKTKWLY RPMNOMQLTLWMZN[ RNbVb RRaOb RR`Pb RS`Tb RRaUb",
	3168: " 30I[JQKOMMOMPNQPQTO[ RPNPTN[ RPPOTM[O[ RYOYNXNXPZPZNYMWMUNSPQT",
	3169: " 47J[XPXOWOWQYQYOXNUMRMONNONQOSQTTUVVWX RONNQ RORQSTTVU RWVVZ RNOOQQRTSVTWVWXVZS[P[MZLYLWNWNYMYMX",
	3170: " 23KYTFQQPUPXQZR[T[VYWW RUFRQQUQZ RTFVFRTQX RNMXM",
	3171: " 42F^GQHOJMLMMNNPNSLX RMNMRLVLZ RMPKUKXLZN[P[RZTXVU RXMVUVXWZX[Z[\\Y]W RYMWUWZ RXMZMXTWX",
	3172: " 29H\\IQJOLMNMONPPPSNX RONORNVNZ ROPMUMXNZP[R[TZVXXUYQYMXMXNYP",
	3173: " 48CaDQEOGMIMJNKPKSIX RJNJRIVIZ RJPHUHXIZK[M[OZQXRU RTMRURXSZU[W[YZ[X]U^Q^M]M]N^P RUMSUSZ RTMVMTTSX",
	3174: " 51G]JQLNNMPMRNSPSR RPMQNQRPVOXMZK[I[HZHXJXJZIZIY RRORRQVQY RZOZNYNYP[P[NZMXMVNTPSRRVRZS[ RPVPXQZS[U[WZYW",
	3175: " 49G]HQIOKMMMNNOPOSMX RNNNRMVMZ RNPLULXMZO[Q[SZUXWT RYMU[T^RaPb RZMV[T_ RYM[MW[U_SaPbMbKaJ`J^L^L`K`K_",
	3176: " 39H\\YMXOVQNWLYK[ RXOOOMPLR RVORNONNO RVORMOMMOLR RLYUYWXXV RNYRZUZVY RNYR[U[WYXV",
	3200: " 50H\\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF RNHMJLNLSMWNY RVYWWXSXNWJVH RQFOGNIMNMSNXOZQ[ RS[UZVXWSWNVIUGSF",
	3201: " 28H\\QHQ[ RRHRZ RSFS[ RSFPINJ RM[W[ RQZO[ RQYP[ RSYT[ RSZU[",
	3202: " 62H\\LJLKMKMJLJ RLIMINJNKMLLLKKKJLHMGPFTFWGXHYJYLXNUPPRNSLUKXK[ RWHXJXLWN RTFVGWJWLVNTPPR RKYLXNXSYWYYX RNXSZWZXY RNXS[W[XZYXYV",
	3203: " 76H\\LJLKMKMJLJ RLIMINJNKMLLLKKKJLHMGPFTFWGXIXLWNTO RVGWIWLVN RSFUGVIVLUNSO RQOTOVPXRYTYWXYWZT[P[MZLYKWKVLUMUNVNWMXLX RWRXTXWWY RSOUPVQWTWWVZT[ RLVLWMWMVLV",
	3204: " 28H\\SIS[ RTHTZ RUFU[ RUFJUZU RP[X[ RSZQ[ RSYR[ RUYV[ RUZW[",
	3205: " 55H\\MFKPMNPMSMVNXPYSYUXXVZS[P[MZLYKWKVLUMUNVNWMXLX RWPXRXVWX RSMUNVOWRWVVYUZS[ RLVLWMWMVLV RMFWF RMGUG RMHQHUGWF",
	3206: " 69H\\VIVJWJWIVI RWHVHUIUJVKWKXJXIWGUFRFOGMILKKOKULXNZQ[S[VZXXYUYTXQVOSNQNOONPMR RNIMKLOLUMXNY RWXXVXSWQ RRFPGOHNJMNMUNXOZQ[ RS[UZVYWVWSVPUOSN",
	3207: " 43H\\KFKL RYFYIXLTQSSRWR[ RSRRTQWQ[ RXLSQQTPWP[R[ RKJLHNFPFUIWIXHYF RMHNGPGRH RKJLINHPHUI",
	3208: " 79H\\PFMGLILLMNPOTOWNXLXIWGTFPF RNGMIMLNN RVNWLWIVG RPFOGNINLONPO RTOUNVLVIUGTF RPOMPLQKSKWLYMZP[T[WZXYYWYSXQWPTO RMQLSLWMY RWYXWXSWQ RPONPMSMWNZP[ RT[VZWWWSVPTO",
	3209: " 69H\\MWMXNXNWMW RWOVQURSSQSNRLPKMKLLINGQFSFVGXIYLYRXVWXUZR[O[MZLXLWMVNVOWOXNYMY RMPLNLKMI RVHWIXLXRWVVX RQSORNQMNMKNHOGQF RSFUGVIWLWSVWUYTZR[",
	3210: " 16MXRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	3211: " 24MXTZS[R[QZQYRXSXTYT\\S^Q_ RRYRZSZSYRY RS[T\\ RTZS^",
	3212: " 32MXRMQNQORPSPTOTNSMRM RRNROSOSNRN RRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	3213: " 40MXRMQNQORPSPTOTNSMRM RRNROSOSNRN RTZS[R[QZQYRXSXTYT\\S^Q_ RRYRZSZSYRY RS[T\\ RTZS^",
	3214: " 34MXRFQGQIRQ RRFRTST RRFSFST RSFTGTISQ RRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	3215: " 52I\\MKMJNJNLLLLJMHNGPFTFWGXHYJYLXNWOSQ RWHXIXMWN RTFVGWIWMVOUP RRQRTSTSQRQ RRXQYQZR[S[TZTYSXRX RRYRZSZSYRY",
	3216: " 24MXTFRGQIQLRMSMTLTKSJRJQK RRKRLSLSKRK RRGQK RQIRJ",
	3217: " 24MXTHSIRIQHQGRFSFTGTJSLQM RRGRHSHSGRG RSITJ RTHSL",
	3218: " 74E_[O[NZNZP\\P\\N[MZMYNXPVUTXRZP[L[JZIXIUJSPORMSKSIRGPFNGMIMLNOPRTWWZY[[[\\Y\\X RKZJXJUKSLR RRMSI RSKRG RNGMK RNNPQTVWYYZ RN[LZKXKULSPO RMINMQQUVXYZZ[Z\\Y",
	3219: " 56H\\PBP_ RTBT_ RXKXJWJWLYLYJXHWGTFPFMGKIKLLNOPURWSXUXXWZ RLLMNOOUQWRXT RMGLILKMMONUPXRYTYWXYWZT[P[MZLYKWKUMUMWLWLV",
	3220: "  8G^[BIbJb R[B\\BJb",
	3221: " 27KYUBSDQGOKNPNTOYQ]S`Ub RQHPKOOOUPYQ\\ RSDRFQIPOPUQ[R^S`",
	3222: " 27KYOBQDSGUKVPVTUYS]Q`Ob RSHTKUOUUTYS\\ RQDRFSITOTUS[R^Q`",
	3223: " 39JZRFQGSQRR RRFRR RRFSGQQRR RMINIVOWO RMIWO RMIMJWNWO RWIVINOMO RWIMO RWIWJMNMO",
	3224: "  8F_JQ[Q[R RJQJR[R",
	3225: " 16F_RIRZSZ RRISISZ RJQ[Q[R RJQJR[R",
	3226: " 16F_JM[M[N RJMJN[N RJU[U[V RJUJV[V",
	3227: " 11NWSFRGRM RSGRM RSFTGRM",
	3228: " 22I[NFMGMM RNGMM RNFOGMM RWFVGVM RWGVM RWFXGVM",
	3229: " 30KYQFOGNINKOMQNSNUMVKVIUGSFQF RQFNIOMSNVKUGQF RSFOGNKQNUMVISF",
	3250: " 58H]TFQGOIMLLOKSKVLYMZO[Q[TZVXXUYRZNZKYHXGVFTF RQHOJNLMOLSLWMY RTYVWWUXRYNYJXH RTFRGPJOLNOMSMXNZO[ RQ[SZUWVUWRXNXIWGVF",
	3251: " 20H]TJO[Q[ RWFUJP[ RWFQ[ RWFTIQKOL RTJRKOL",
	3252: " 52H]OKOJPJPLNLNJOHPGSFVFYGZIZKYMWOMUKWI[ RXGYIYKXMVOSQ RVFWGXIXKWMUOMU RJYKXMXRYWYXX RMXRZWZ RMXR[U[WZXXXW",
	3253: " 64H]OKOJPJPLNLNJOHPGSFVFYGZIZKYMXNVOSP RXGYIYKXMWN RVFWGXIXKWMUOSP RQPSPVQWRXTXWWYUZR[O[LZKYJWJULULWKWKV RVRWTWWVY RSPUQVSVWUYTZR[",
	3254: " 15H]WJR[T[ RZFXJS[ RZFT[ RZFJUZU",
	3255: " 49H]QFLP RQF[F RQGYG RPHUHYG[F RLPMOPNSNVOWPXRXUWXUZQ[N[LZKYJWJULULWKWKV RVPWRWUVXTZ RSNUOVQVUUXSZQ[",
	3256: " 61H]YJYIXIXKZKZIYGWFTFQGOIMLLOKSKVLYMZO[R[UZWXXVXSWQVPTOQOOPNQMS RPINLMOLSLWMY RVXWVWSVQ RTFRGPJOLNOMSMXNZO[ RR[TZUYVVVRUPTO",
	3257: " 39H]NFLL R[FZIXLTQRTQWP[ RRSPWO[ RXLRRPUOWN[P[ RMIPFRFWI ROGRGWI RMIOHRHWIYIZH[F",
	3258: "104H]SFPGOHNJNMOOQPTPWOYNZLZIYGWFSF RUFPG RPHOJONPO ROORP RSPWO RXNYLYIXG RYGUF RSFQHPJPNQP RTPVOWNXLXHWF RQPMQKSJUJXKZN[R[VZWYXWXTWRVQTP RRPMQ RNQLSKUKXLZ RKZP[VZ RVYWWWTVR RVQSP RQPOQMSLULXMZN[ RR[TZUYVWVSUQTP",
	3259: " 61H]XNWPVQTRQROQNPMNMKNIPGSFVFXGYHZKZNYRXUVXTZQ[N[LZKXKVMVMXLXLW ROPNNNKOI RXHYJYNXRWUUX RQRPQOOOKPHQGSF RVFWGXIXNWRVUUWSZQ[",
	3260: " 16MXPXOYOZP[Q[RZRYQXPX RPYPZQZQYPY",
	3261: " 22MXQ[P[OZOYPXQXRYR[Q]P^N_ RPYPZQZQYPY RQ[Q\\P^",
	3262: " 32MXSMRNROSPTPUOUNTMSM RSNSOTOTNSN RPXOYOZP[Q[RZRYQXPX RPYPZQZQYPY",
	3263: " 38MXSMRNROSPTPUOUNTMSM RSNSOTOTNSN RQ[P[OZOYPXQXRYR[Q]P^N_ RPYPZQZQYPY RQ[Q\\P^",
	3264: " 34MXVFUFTGRT RVGUGRT RVGVHRT RVFWGWHRT RPXOYOZP[Q[RZRYQXPX RPYPZQZQYPY",
	3265: " 59H]OKOJPJPLNLNJOHPGSFWFZG[I[KZMYNWOSPQQQSSTTT RUFZG RYGZIZKYMXNVO RWFXGYIYKXMWNSPRQRSST RPXOYOZP[Q[RZRYQXPX RPYPZQZQYPY",
	3266: " 22MXWFUGTHSJSLTMUMVLVKUJTJ RUGTITJ RTKTLULUKTK",
	3267: " 22MXVIUITHTGUFVFWGWIVKULSM RUGUHVHVGUG RVIVJUL",
	3268: " 72E_\\O\\N[N[P]P]N\\M[MYNWPRXPZN[K[HZGXGVHTISKRPPROTMUKUITGRFPGOIOLPRQURWTZV[X[YYYX RL[HZ RIZHXHVITJSLR RPPQSTYVZ RK[JZIXIVJTKSMRRO ROLPOQRSVUYWZXZYY",
	3269: " 52H]TBL_ RYBQ_ RZKZJYJYL[L[JZHYGVFRFOGMIMLNNPPVSWUWXVZ RNLONVRWT ROGNINKOMUPWRXTXWWYVZS[O[LZKYJWJULULWKWKV",
	3270: "  8G^_BEbFb R_B`BFb",
	3271: " 32JZZBXCUERHPKNOMSMXN\\O_Qb RSHQKOONTN\\ RZBWDTGRJQLPOOSN\\ RNTO]P`Qb",
	3272: " 32JZSBUEVHWLWQVUTYR\\O_LaJb RVHVPUUSYQ\\ RSBTDUGVP RVHUQTUSXRZP]M`Jb",
	3273: " 39J[TFSGUQTR RTFTR RTFUGSQTR ROIPIXOYO ROIYO ROIOJYNYO RYIXIPOOO RYIOO RYIYJONOO",
	3274: "  8F_JQ[Q[R RJQJR[R",
	3275: " 16F_RIRZSZ RRISISZ RJQ[Q[R RJQJR[R",
	3276: " 16F_JM[M[N RJMJN[N RJU[U[V RJUJV[V",
	3277: " 11MWUFTGRM RUGRM RUFVGRM",
	3278: " 22H\\PFOGMM RPGMM RPFQGMM RZFYGWM RZGWM RZF[GWM",
	3279: " 30KZSFQGPIPKQMSNUNWMXKXIWGUFSF RSFPIQMUNXKWGSF RUFQGPKSNWMXIUF",
	3301: " 62F^IHJIIJHIIGKFMFOGPHQKQOPRNTLUIV ROHPKPPOR RMFNGOJOPNSLU RLVOY RKVOZ RIVN[UV R\\G[H\\H\\G[FYFWGVHUJUYW[[W RWHVJVXXZ RYFXGWJWWYY",
	3302: "101E_GQGRHSJSLRLOKMIJIHKF RKOIK RJSKRKPIMHKHIIGKFNFPGQHRJRRQUOW RPHQJQT RNFOGPJPUOW RRISGUFWFYGZH[J\\K RYHZJ RWFXGYJZK\\K R\\KRP RYM[O\\R\\U[XYZV[S[PZJWIWHX RXNYN[P RVNYO[Q\\S RTZRZLWKW RZYXZUZRYNWKVIVHXHZI[JZIY",
	3303: " 79F^RHPFNFLGJJINIRJVLYNZQ[T[WZYY[W RLHKJJMJRKVMYPZ RNFMGLIKMKQLUMWOYRZUZXY[W RUFRHQIPKPLQNTPURUT RQKQLUPUQ RQIQJRLUNVPVRUTSURUPTOR RUFVGXHZH RUGVHWH RTGVIXIZH[G",
	3304: " 79E_HLHKIIKGNFRFUGWHYJ[M\\Q\\U[XYZV[S[PZJWIWHX RKHMGRGUHWIYK[N RTZRZLWKW RHKJIMHRHUIWJYL[O\\R RZYXZUZRYNWKVIVHXHZI[JZIY RPHMKLMLONSNU RMNMONQNR RMKMMOQOSNUMVKVJUJT",
	3305: " 95F^RHPFNFLGJJINIRJVLYNZQ[T[WZYY[W RLHKJJMJRKVMYPZ RNFMGLIKMKQLUMWOYRZUZXY[W RUFRHQIPKPLQNTPURUT RQKQLUPUQ RQIQJRLUNVPVRUTSURUPTOR RUFVGXHZH RUGVHWH RTGVIXIZH[G RUNYK RYKZL\\L RXLYMZM RWMXNZN\\L",
	3306: " 94F^MNKMJKJIKGNFQFTGXI RKHMGRGUH RJKKIMHRHXIZI[H[GZFYF RSHRIQKQMROVSWVWYV\\U]S^ RTPWSXVXYW[ RQMSOVQXSYVYYX[V]S^O^L]K\\JZJWLTLRKQ RL\\K[KWLU RO^M]L[LWMTMRLQJQIRIS RUPYL RYLZM\\M RXMYNZN RWNXOZO\\M",
	3307: " 99E_UJTHSGQFNFKGIJHNHRIUJWLYNZQ[T[WZYY[W\\T\\Q[NYL RKHJJIMIRJUKW RZW[U[QZNYM RNFLGKIJMJRKVLXNZ RWZYXZUZQYOWM RUFRHPJOLOMPOSQTSTU RPLPMTQTR RPJPKQMTOUQUSTURVQVOUNS RTOYLZJ R\\FZJ RYG]I R\\F[GYGZHZJ[I]I\\H\\F",
	3308: " 92F_RFPGNIMKMMNOPQQSQU RNLNMQQQR RNINKOMQORQRSQUPVNWLWJVIUHSHQIPJQIR RRFTHVHXG RQGSH RPGQHSIUIXG RRPYK RYK[N\\Q\\T[WYYVZR[ RXLZN[Q[UZW RVMWMYOZRZVYXXYVZ RVZTZRYPYNZM\\N^P_R_T^ RSZQZ RR[PZNZ",
	3309: " 83F_PPNPLOKNJLJJKHLGOFQFTGWJYK RLHNGRGTHUI RJJKIMHQHTIVJYK[K\\J\\H[GYG RJXKYJZIYIWJVLVNWPYR\\T^ RNXOYQ\\R] RLVMWNYP\\Q]S^V^X]Y\\ZZZWYUWRVPVO RYXYWVRVQ RX]Y[YYXWVTURUPWNYNZOZP",
	3310: " 83F_PPNPLOKNJLJJKHLGOFQFTGWJYK RLHNGRGTHUI RJJKIMHQHTIVJYK[K\\J\\H[GYG RJXKYJZIYIWJVLVNWPYR\\T^ RNXOYQ\\R] RLVMWNYP\\Q]S^V^X]Y\\ZZZWYUWRVPVO RYXYWVRVQ RX]Y[YYXWVTURUPWNYNZOZP",
	3311: " 81E_[KZIXGUFRFOGMILKLNMQPWPYN[ RMNMOPUPV RNHMJMMNOPSQVQXPZN[L[JZ RHVJZ RGYKW RHVHXGYIYJZJXKWIWHV RNONMOKQJTJVKXMYM RUKWM RRJTKULVN RYMPQ RUOYXZY[Y RTPXXZZ RSPWYY[\\X",
	3312: " 73G^ZSYTVTUSUQVOXLYJYH RVQVPYLYK RWTVSVRWPYNZLZJYHXGUFPFMGLHKJKLLNNQOSOTNV RLKLLOQOR RLHLJMLOOPQPSOUMWJY RMWOWRYUZXZZY RNXOXSZTZ RJYLXMXQZT[V[YZZY[W",
	3313: "128BbEQERFSHSJRJOIMGJGHIF RIOGK RHSIRIPGMFKFIGGIFKFMGOIPLPROUNWLYI[HZGZ RNIOLORNUMW RJZIYHY RKFMHNKNRMVLXKYJXIXF[ RNGPFRFTGVIWLWRVUUWSYQ[PZOZ RUIVLVRUV RRZQYPY RRFTHUKUSTWSYRXQXN[ RUHVGXFZF\\G]H^J_K R\\H]J RZF[G\\J]K_K R_K\\M[NZQZT[X][`X R\\N[P[T\\W^Z R_K]M\\O\\S]W_Y",
	3314: " 96D`GQGRHSJSLRLOKMIJIHKF RKOIK RJSKRKPIMHKHIIGKFNFPGRISLSRRUQWOYL[KZIZG[ RQIRKRRQUPWOX RMZKYIY RNFPHQKQRPVNYLXJXG[ RRHSGUFWFYGZH[J\\K RYHZJ RWFXGYJZK\\K R\\KYMXNWQWTXXZ[]X RYNXPXTYW[Z R\\KZMYOYSZW\\Y",
	3315: " 72D`PFNGLIKKKMMQMS RLLLMMOMP RLILKNONQMSLTJTISIR RPFQGWIZK[M\\P\\S[VZXXZU[R[OZIWHWGX RPGQHWJYKZL RPFPHQIWKYL[N\\P RSZQZKWJW RYYWZTZQYMWJVHVGXGZH[IZHY",
	3316: "100E`HQHRISKSMRMOLMJJJHLF RLOJK RKSLRLPJMIKIIJGLFOFQGRHSJSU RSWS\\R^P_M_L^L\\M[N\\M] RQHRJR\\Q^ ROFPGQJQU RQWQ\\P^O_ RSJXF RXFZI[K\\O\\R[UYXV[ RWGZK[N[O RVHXJZM[P[SZVYX RWYUVSU RQUOVMX RWZUWSVPV RV[TXSW RQWOWMX",
	3317: " 88D`PFNGLIKKKMMQMS RLLLMMOMP RLILKNONQMSLTJTISIR RPFQGWIZK[M\\P\\S[VZX RXZU[R[OZIWHWGX RPGQHWJYKZL RPFPHQIWKYL[N\\P RSZQZKWJW RXZTZQYMWJVHVGXGZH[IZHY RTXVVXV\\Z]Z RWWXW[Z RUWVWZ[\\[^Y",
	3318: " 96D`GQGRHSJSLRLOKMIJIHKF RKOIK RJSKRKPIMHKHIIGKFNFPGQHRJRVQXOZM[K[IZ RPHQJQVPX RNFOGPJPVOYM[ RGVIZ RFYJW RGVGXFYHYIZIXJWHWGV RRISGUFWFYGZH[J\\K RYHZJ RWFXGYJZK\\K R\\KRP RTOXYZ[]X RUOYX[Z RVNZX[Y\\Y",
	3319: " 83E`\\H[G\\F]G]I\\KZKVISHOHKIIK RYJVHSGOGLH R]I\\JZJVGSFOFLGJIIKHNHRIUJWLYNZQ[U[XZZY\\W]T]Q\\OZNWNUOSRQSOS RLXNYQZUZYY RIUKWMXPYUYYX[W\\V]T RXOWOSSRS R]Q[OYOWPUSSTQTOSNQNOOMQL",
	3320: " 81F_LNJMIKIIJGMFRFUGYJ[J\\I RJHLGRGUHXJ RIKJILHRHUIYK[K\\I\\G[FZG[H RUIRLQNQPSTSV RRORPSRSS RRLRNTRTTSVRWPWOVOT RJYKZJ[IZIXJVLVOWSYVZYZ[Y RLWMWSZUZ RIXJWKWMXQZT[W[ZZ\\X",
	3321: " 45G]JHKHLILWJX RKGMHMXPZ RIILFNHNWPYRY RJXKXMYO[RYVV RTHUHVIVYX[[X RUGWHWYYZ RSIVFYHXIXXYYZY",
	3322: "100D`GQGRHSJSLRLOKMIJIHKF RKOIK RJSKRKPIMHKHIIGKFNFPGQHRJRRQUOW RPHQJQT RNFOGPJPUOW RRISGUFWFYG[J\\K RYHZJ RWFXGYJZK\\K RZKXKWLWNXP[R\\T RXO[Q RWMXN[P\\R\\V[XYZW[S[PZJWIWHX RTZRZLWKW RZYXZUZRYNWKVIVHXHZI[JZIY",
	3323: "143BcEQERFSHSJRJOIMGJGHIF RIOGK RHSIRIPGMFKFIGGIFLFNGOHPJPNOQMTKV RNHOJOONR RLFMGNJNOMSKV RNGPFSFUG RWFTGSISMTPVSWUWWVY RTMTNWSWT RWFUGTITLUNWQXTXVWXUZS[O[MZKXIWGWFX RNZKWJW RQ[OZLWJVGVFXFZG[HZGY RWFZF\\G^J_K R\\H]J RZF[G\\J]K_K R]K[KZLZN[P^R_T R[O^Q RZM[N^P_R_W^Y]Z[[X[UZ RYZXZVY R^Y\\ZZZXYWX",
	3324: " 86F^KHMHOIPJQMQO RQQQUPXM[KZI[ RNZLYKY ROYNYLXI[ RMGPHQIRLRUSWUYWZ RIINFPGRISLSO RSQSTTWUXWYYY RQURXTZV[[X RSLTIWFYG[F RVGXHYH RUHVHXI[F RKSMOQO RSOWOYM RMPWP RKSMQQQ RSQWQYM",
	3325: " 74E_HQHRISKSMRMOLMJJJHLF RLOJK RKSLRLPJMIKIIJGLFOFQGRHSJSORRQTQUSWTW RQHRJRPQSPUSX ROFPGQJQPPTOVRYUV RSJ[F RYGYZX] RZGZXY[ R[F[VZZY\\W^T_P_M^K\\JZKYLZK[",
	3326: " 74F^NIOGQFTFVGWHXJXMWOVPTQ RQQOPNN RVHWIWNVO RTFUGVIVNUPTQ RMUNSORQQTQWRYTZVZZY\\W^T_P_N^KZJY RXTYVYZX\\ RTQWSXUX[W]V^T_ RO^N]LZKY RR_P^O]MZLYIYHZH\\I]J]",
	3401: " 46J[TMQNOONPMSMVNYO[UX RNVOYPZ RQNOPNSNUOXQZ RRNSOUPUYW[ZX RSNVPVXXZ RTMUNWOXO RWPXO RWPWXXYYY",
	3402: " 50J[LHMINK RTFQGOINKNXMY RPIOKOXRZ RTFRGQHPKPXRYSZ RMYNYPZQ[TZ RPPVMWOXRXUWXVYTZ RUNVOWQ RTNVPWSWUVXTZ",
	3403: " 27KXRNTPVOTMRNOPNRNWOYQ[UY RSNUO RPPOROWPYQZ RQOPQPVQXSZ",
	3404: " 47J[QFNINKOLSNVPWRWUVXTZ ROJOKSMVOWP ROHOIPJUMWOXRXUWXTZQ[ RRNNPNXMY ROPOXRZ RPOPXRYSZ RMYNYPZQ[",
	3405: " 27KXPUVQSMOPNRNWOYQ[UY RUQRN RPPOROWPYQZ RTRROQOPQPVQXSZ",
	3406: " 49LYXFWGUGSFQFPHPMOONP RVHTHRGQG RXFWHVITIRHQHPI RPKQMRNTOVOVP RNPPP RRPVP RPPPTQ` RSOPOQNQ[ RRPRTQ`",
	3407: " 53J[TMQNOONPMSMVNYO[UX RNWOYPZ RQNOPNSNUOXQZ RRNSOUPUXV[V]U_ RSNVPVZ RTMUNWOXO RWPXO RWPW\\V^U_S`P`N_M^M]N]N^",
	3408: " 50J[LHMINK RTFQGOINKNXMY RPIOKOYPZ RTFRGQHPKPXQYRY RMYOZP[SX RPPVMWOXSXWWZV\\T^Q` RUNVOWR RTNVQWTWWV[T^",
	3409: " 39MWRFQGQHRISHSGRF RQGSH RQHSG ROOPOQPQYS[VX RPNRORXTZ RNPQMRNTO RSPTO RSPSXTYUY",
	3410: " 45MWRFQGQHRISHSGRF RQGSH RQHSG ROOPOQPQ[P^O_M` RPNROR[Q] RNPQMRNTO RSPTO RSPS[R]P_M` RS[T]U^",
	3411: " 63KYNHOIPK RUFSGQIPKPMOONP RPPPXOY RRIQKQM RQOPOQMQXSZ RUFSHRKRO RRPRXSYTY ROYQZR[UX RRLVIWJWLUNSO RUJVKVLUN RROWOWP RNPPP RRPWP",
	3412: " 29MWOHPIQK RWFTGRIQKQXPY RSIRKRYTZ RWFUGTHSKSXTYUY RPYRZS[VX",
	3413: " 74E_GOHOIPIXHYJ[ RHNJPJXIYJZKYJX RFPIMKOKXLYJ[ RNNPOQQQXPYR[ RPNQORQRXQYRZSYRX RKPNNPMRNSPSXTYR[ RVNWOYPYY[[^X RWNZPZX\\Z RSPVNXMYN[O\\O R[P\\O R[P[X\\Y]Y",
	3414: " 49I[KOLOMPMXLYN[ RLNNPNXMYNZOYNX RJPMMOOOXPYN[ RRNSOUPUYW[ZX RSNVPVXXZ ROPRNTMUNWOXO RWPXO RWPWXXYYY",
	3415: " 41J[NPNXMY ROPOXRZ RQOPPPXRYSZ RMYNYPZQ[TZ RNPQOVMWOXRXUWXVYTZ RUNVOWQ RTNVPWSWUVXTZ",
	3416: " 57J[OJMLMNNQNXLZ RNYO` RNMNNOQO[ RNKNLONPQPXQXSYTZ RPYO` RSZQY RTZR[PY RNYLZ RPPVMWOXRXUWXVYTZ RUNVOWQ RTNVPWSWUVXTZ",
	3417: " 43J[TMQNOONPMSMVNYO[UX RNWOYPZ RQNOPNSNUOXQZ RRNSOUPUXV` RSNVPV[ RTMUNWOXO RWPXO RWPWXV`",
	3418: " 32KYNOOOPPPXOY RONQPQYSZ RMPPMRORXSYTY ROYQZR[UX RTNUPWOVMRO RUNVO",
	3419: " 42LWXFWGUGSFQFPHPMOONP RVHTHRGQG RXFWHVITIRHQHPI RPKRP RPPPTQ` RQOPOQNQ[ RRPRTQ` RNPPP",
	3420: " 37LXSIRLQNPONP RSISOVOVP RNPQP RSPVP RQPQXPY RROQORMRXTZ RSPSXTYUY RPYRZS[VX",
	3421: " 47I[KOLOMPMXLY RLNNPNXPZ RJPMMOOOXQYRZ RLYMYOZP[RZUX RVMTOUPUYW[ZX RVPWOVNUOVPVXXZ RVMXOWPWXXYYY",
	3422: " 47J[OKMMMONRNXMY RNNNOOROXRZ RNLNMOOPRPXRYSZ RMYNYPZQ[TZ RPPVMWOXRXUWXVYTZ RUNVOWQ RTNVPWSWUVXTZ",
	3423: " 72F_KKIMIOJRJXIYK[ RJNJOKRKXJYKZLYKX RJLJMKOLRLXMYK[ RONQORQRXQY RQNROSQSXVZ RLPONQMSNTPTXVYWZ RQYRYTZU[XZ RTPZM[O\\R\\T[XZYXZ RYNZO[Q RXNZP[S[UZXXZ",
	3424: " 44KZOOPOQPQXPXNYM[M]N_P`S`V_V^U^U_ RPNRPRXUZ RNPQMSOSXUYVZ RXYT[SZQYOYM[ RUNVPXOWMSO RVNWO",
	3425: " 47J[OKMMMONRNXMY RNNNOOROYQZ RNLNMOOPRPXQYRY RMYOZP[SX RPPVMWOXSXWWZV\\T^Q` RUNVOWR RTNVQWTWWV[T^",
	3426: " 43KYNPSMUNVPVRUTQV RSNUO RRNTOUQURTTSU RSUUWVYV]U_S`Q`O_N]N[OYQXWV RRVTWUY RQVTXUZU]T_S`",
	3427: " 61JZRMPNMPMRNU RNPNROT RPNOOORPT RPNROTOVNWMWKVJTJ RQNSN RRMTNVN RNUVRWUWWVYR[ RUSVUVXUY RTSUUUXTZ RTZRYOYL[ RSZQZ RR[PZNZL[",
	3428: " 78J[VFUGSGQFOFNHNMMOLP RTHRHPGOG RVFUHTIRIPHOHNI RNKPP RNPNTO` ROONOONO[ RPPPTO` RLPNP RPPUMWNXPXRWTSV RUNWO RTNVOWQWRVTUU RUUWVXXX[W]U_R` RUVWW RSVTVVWWYW\\V^",
	3429: " 62J[PIOLNNMOKP RPIPXQYO[ ROONOONOXNYOZPYOX RKPNPNXMYO[ RPPUMWNXPXRWTSV RUNWO RTNVOWQWRVTUU RUUWVXXX[W]U_R` RUVWW RSVTVVWWYW\\V^",
	3501: " 60G]LINGPFRFSGZW[X]X RQGRHYXZZ[YYX RNGPGQHXXYZZ[[[]X RLMMLOKPKQL RPLPM RMLOLPN RG[IYKXNXPY RJYNYOZ RG[JZMZN[PY RRJLX RNSVS",
	3502: "110F^HHJFMFOGQF RKGNG RHHJGLHOHQF RMKLLKNKOIOHPHRIQKQKW RLMLU RIPLP RMKMTLVKW RRIQJPLPU RQKQS RRIRRQTPU RRIXFZG[I[KYMUO RXGZIZK RVGXHYIYLWN RWNZP[R[X RYPZRZW RWNXOYQYX RJ[MYPXTXWY RLZOYTYVZ RJ[NZSZU[WYYX[X RUOUX RURYR RUUYU",
	3503: " 69E]NGLHJJILHOHSIVJXMZP[S[VZXYZW[U RJKINISKWNYQZTZWY RNGLIKKJNJRKUNXQYTYWXYW[U RPJPV RQJQT RRIRSQUPV RPJRIUFWGYGZF RTGVHXH RSHUIWIYHZF RWIWX",
	3504: " 72G^IFWFYGZIZX RKGWGYIYW RIFJGLHWHXIXX ROKNLMNMOKOJPJRKQMQMV RNMNT RKPNP ROKOSNUMV RI[LYOXSXVY RKZNYSYUZ RI[MZRZT[VYXXZX RRHRX RRMTNVNXM RRSTRVRXS",
	3505: " 94G]IHKFMFOGQF RLGNG RIHKGMHOHQF RNKMLLNLOJOIPIRJQLQLW RMMMU RJPMP RNKNTMVLW RQMRJSHTGVFXF[G RTHVGXGZH RRJSIUHWHYI[G RQURRSPTOVOXP RTPVPWQ RRRSQUQVRXP RK[NYRXWX[Y RMZPYWYZZ RK[OZVZY[[Y RQMQX",
	3506: " 91F]JHLFOFQGSF RMGPG RJHLGNHQHSF RPKOLNNNOLOKPKRLQNQNV ROMOT RLPOP RPKPSOUNV RSJSYRZQZMXKXIYG[ RTJTX RTPXP RPZOZMYJY RUIUOXO RXQUQUWTYP[N[LZJZG[ RSJUIXFZG\\G]F RWGYH[H RVHXIZI\\H]F RXIXW",
	3507: " 87E^NGLHJJILHOHRIUJWLYNZQ[U[XZZX[V[SZQYPWOUO RJKINISJV RNGLIKKJNJSKVLXNZ RYXZWZSYQ RU[WZXYYWYSXQWPUO RPJPW RQJQU RRIRTQVPW RPJRIUFWGYGZF RTGVHXH RSHUIWIYHZF RYHUOU[ RUSYS RUVYV",
	3508: "112F^HHJFMFOGQF RKGNG RHHJGLHOHQF RMKLLKNKOIOHPHRIQKQKW RLMLU RIPLP RMKMTLVKW RJ[MYPXSXUY RLZOYRYTZ RJ[NZQZS[UY RRIQJPLPU RQKQS RRIRRQTPU RRITGVFXFZG RWGXGYH RTGVGXIZG RUOWNYLZM[P[TZXX[ RXMYNZPZUYX RWNXNYPYUX[ RUOUY RURYR RUUYU",
	3509: " 67I\\LHNFQFTGVF ROGSG RLHNGQHTHVF RSKRLQNQOOONPNROQQQQV RRMRT ROPRP RSKSSRUQV RYHWJVMVXUZSZOXMXKYI[ RWKWW RRZQZOYLY RYHXJXVWXUZS[P[NZKZI[",
	3510: " 65H\\LHNFQFTGVF ROGSG RLHNGQHTHVF RSKRLQNQOOONPNROQQQQV RRMRT ROPRP RSKSSRUQV RYHWJVMVXUZ RWKWW RYHXJXVWXUZR[O[LZJXJVKULUMVLWKW RJVMV",
	3511: "115F^HHJFMFOGQF RKGNG RHHJGLHOHQF RMKLLKNKOIOHPHRIQKQKW RLMLU RIPLP RMKMTLVKW RJ[MYPXSXUY RLZNYRYTZ RJ[NZQZS[UY RRIQJPLPU RQKQS RRIRRQTPU RRITGVFXFZG RWGXGYH RTGVGXIZG RUOXLYM[N RWMYN[N R[NYQWSUU RWSYTZX[Z\\Z RYVZZ RWSXTYZZ[[[\\Z RUOUY",
	3512: " 85G]IHKFNFPGRF RLGOG RIHKGMHPHRF RNKMLLNLOJOIPIRJQLQLW RMMMU RJPMP RNKNTMVLW RK[NYRXWX[Y RMZPYWYZZ RK[OZVZY[[Y RSIRJQLQU RRKRS RSISRRTQU RSIUGWFYF[G RXGYGZH RUGWGYI[G RWGWX",
	3513: "107D`LJKKJMJOHOGPGRHQJQJU RKLKS RHPKP RLJLRKTJU RE[GYIXKXMYNYOX RHYKYMZ RE[GZJZL[M[NZOX RLJPFTJTWUYVY RPGSJSXRYSZTYSX RPPSP RNHOHRKROOO ROQRQRXQYS[VYWX RTJXF\\J\\W]Y^Y RXG[J[X]Z RXP[P RVHWHZKZOWO RWQZQZY\\[^Y ROHOX RWHWX",
	3514: " 84E^GIIGKFMFOGQJVUXXYY RMGOIPKVWYZ RIGKGMHOKTVVYWZY[ RVHXIZI\\H]F RWGYH[H RVHXFZG\\G]F RKOIOHPHRIQKQ RIPKP RG[IYKXNXPY RJYMYOZ RG[JZMZN[PY RKGKX RYIY[ RRLSMUNWNYM RKTMSQSST",
	3515: " 79E_NFLGJIIKHNHRIUJWLYNZQ[S[VZXYZW[U\\R\\N[KZIXGVFUGRIOJ RJJIMISJV RNFLHKJJMJSKVLXNZ RZV[S[MYIXH RVZXXYVZSZMYKWHUG ROJOW RPJPU RQJQTPVOW RUGUZ RUMWNXNZM RUSWRXRZS",
	3516: " 70H^KFLGMIMOKOJPJRKQMQMYJ[MZMbO` RMHNJN` RKPNP RKFMGNHOJO` ROKRIVFZJZX RVGYJYX RTHUHXKXY RRXUXXY RSYUYWZ RRZTZV[XYZX RRIR_ RRMTNVNXM RRSTRVRXS",
	3517: " 99E_NFLGJIIKHNHRIUJWLYNZP[T[VZXYZW[U\\R\\N[KZIXGVFUGRIOJ RJJIMISJV RNFLHKJJMJSKVLXNZ RZV[S[MYIXH RVZXXYVZSZMYKWHUG ROJOW RPJPU RQJQTPVOW RUGUZ RUMWNXNZM RUSWRXRZS RP[QZRZT[X`Za[a RT\\V_XaYa RRZS[VaXbZb[a",
	3518: "108F^HHJFMFOGQF RKGNG RHHJGLHOHQF RMKLLKNKOIOHPHRIQKQKW RLMLU RIPLP RMKMTLVKW RJ[MYPXRXUY RLZNYRYTZ RJ[NZQZS[UY RRIQJPLPU RQKQS RRIRRQTPU RRIUGWFYGZIZLYNXOTQRR RWGXGYIYMXN RUGWHXJXMWOTQ RTQVRWSZX[Y\\Y RWTYX[Z RTQVSXYZ[\\Y",
	3519: " 94G^UITHRGOF RVHTG RWGSFOFLGKHJJKLLMONWNYOZPZRYU RKKLLOMXMZN[O[QZS RKHKJLKOLYL[M\\O\\QYUU[ RIOJPLQUQVRVSUU RJQLRTRUS RIOIPJRLSSSUTUU RI[LYPXSXVY RKZNYRYUZ RI[MZRZU[ RWGUISL RRNPQ ROSMUKVJVJUKV",
	3520: " 71E]JJILHOHSIVKYMZP[S[VZXYZW[U RISJVLXNYQZTZWY RJJIMIQJTLWNXQYTYWXYW[U RHIIGKFOFUGYG[F RPGTHXH RHIIHKGNGTIWIYH[F RSIRJPKPV RQKQT RRJRSQUPV RWIWX",
	3521: " 89F^HHJFLFOGQF RKGNG RHHJGMHOHQF RKJJLIOISJVKXMZP[S[VZXYZ[\\Y RJSKVNYQZTZ RKJJNJQKTLVNXQYUYXX RUIQJPLPV RQKQT RRJRSQUPV RUIWHYFZG\\HZIZW[Y\\Y RYIZHYGXHYIYX[Z RWHXIXX RUIUY RUNXN RURXR",
	3522: " 72G^JFKGLILOJOIPIRJQLQLXJY RLHMJMX RJPMP RNYQYSZ RJFLGMHNJNXRXUY RJYMYPZR[UYXXZX RRJUIWHYFZG\\HZIZX RYIZHYGXHYIYW RWHXIXX RRJRX RRMTNVNXM RRSTRVRXS",
	3523: " 95E`HFIGJIJOHOGPGRHQJQJXHY RJHKJKX RHPKP RLYNYPZ RHFJGKHLJLXOXQY RHYKYNZO[QYTXVYW[YY\\X ROHRFTHTXWXYY RRGSHSX ROHQHRIRXQY RWYXZ RWHZF\\H\\X RZG[H[X RWHYHZIZXYY ROHOX RWHWX RONRN RORRR RWNZN RWRZR",
	3524: " 65G]HIJGLFNFOGWYXZZZ RMGNHVYWZ RJGLGMHUZV[X[ZZ\\X RWFYG[G\\F RWGXHZH RVHWIYI[H\\F RH[IYKXMXNY RJYLYMZ RH[IZKZM[ RWFSO RQRM[ RLPPP RSPXP",
	3525: " 86G^JFKGLILOJOIPIRJQLQLXJY RLHMJMX RJPMP RNYQYSZ RJFLGMHNJNXRXUY RJYMYPZR[UYXX RRJUIWHYFZG\\HZIZ^Y`WbUaQ`L` RYIZHYGXHYIYY RWHXIXXZ[ RXaV`S` RY`V_P_L` RRJRX RRMTNVNXM RRSTRVRXS",
	3526: " 57H\\XGWIROOSMWJ[ RVKNV RZFWJUNRRMXLZ RJHLFOGUGZF RKGOHSHWG RJHNIRIVHXG RLZNYRXVXZY RMZQYUYYZ RJ[OZUZX[ZY RMPQP RTPXP",
	3601: " 53J[PRNTMVMXNZP[RYUX RMVNXOYQZ RNTNVOXQYRY RNPPPSOUNVMXOWPWXXYYY RONNOQO RTOWOVNVYWZ RMOOMPNROUPUYW[YY RMORT",
	3602: " 44I[LHMJMXKY RNJMHNGNXQZ RLHOFOXQYRZ RKYMYOZP[RZUYWY ROPROTNUMVNXOYOWPWY RTNVOVX RROSOUPUY",
	3603: " 35JXNONXLYMYOZP[ ROOOYQZ RPOPXRYSYQZP[ RNORNTMUNWOXO RSNTOVO RPORNTPVPXO",
	3604: " 41IZRMPNMOMXKY RNONXQZ RRMOOOXQYRZ RKYMYOZP[RZUYWY RMHPFQIWOWY RPINHOGPIVOVX RMHUPUY",
	3605: " 32JXNONXLYMYOZP[ ROOOYQZ RPOPXRYSYQZP[ RNORNTMWQURPU RSNVQ RPORNUR",
	3606: " 41JWNHNXLYMYOZP[ ROHOYQZ RPHPXRYSYQZP[ RNHQGSFTGVHWH RRGSHUH RPHQGSIUIWH RKMNM RPMTM",
	3607: " 56I[MOMXKYLYNZO[PZRYUX RNPNYPZ ROOOXQYRY RMOOORNTMUNWOYOWPW\\V_TaRbQaO`M` RSNVPV\\ RSaQ`P` RRNSOUPUZV]V_ RTaS`Q_O_M`",
	3608: " 47I[LHMJMXKYLYNZO[ RNJMHNGNYPZ RLHOFOXQYO[ ROPROTNUMVNXOYOWPWYU[T] RTNVOVYU[ RROSOUPUYT]T`UbVbT`",
	3609: " 35MWRFPHRITHRF RRGQHSHRG RRMQNOOQPQYS[UY RRPSORNQORPRYSZ RRMSNUOSPSXTYUY",
	3610: " 39MWRFPHRITHRF RRGQHSHRG RRMQNOOQPQYS[T] RRPSORNQORPRYS[ RRMSNUOSPSYT]T`RbPbPaRb",
	3611: " 50IZLHMJMXKYLYNZO[ RNJMHNGNYPZ RLHOFOXQYO[ ROPRNTMVPSROU RSNUP RRNTQ RSRTSVXWYXY RSSTTUYVZ RRSSTTYV[XY",
	3612: " 22MWPHQJQXOYPYRZS[ RRJQHRGRYTZ RPHSFSXUYVYTZS[",
	3613: " 67E_GOHOIPIXGYHYJZK[ RINJOJYLZ RGOIMKOKXMYK[ RKPNOPNQMSOSXUYS[ RPNRORYTZ RNOOOQPQXPYRZS[ RSPVOXNYMZN\\O]O[P[X\\Y]Y RXNZOZY[Z RVOWOYPYY[[]Y",
	3614: " 45I[KOLOMPMXKYLYNZO[ RMNNONYPZ RKOMMOOOXQYO[ ROPROTNUMVNXOYOWPWXXYYY RTNVOVYWZ RROSOUPUYW[YY",
	3615: " 40I[MOMXKY RNPNXQZ ROOOXQYRZ RKYMYOZP[RZUYWY RMOOORNTMUNWOYOWPWY RSNVPVX RRNSOUPUY",
	3616: " 54I[LMMOMXKYMYMb RMNNONaO`N^ RNYOYQZ RLMNNOOOXQYRZ ROZP[RZUYWY ROZO^P`Mb ROPROTNUMVNXOYOWPWY RTNVOVX RROSOUPUY",
	3617: " 44I[MOMXKY RNPNYPZ ROOOXQYRY RKYLYNZO[PZRYUX RMOOORNTMUNWOYOWPWb RSNVPVaU`V^ RRNSOUPU^T`Wb",
	3618: " 38JXLOMONPNXLYMYOZP[ RMNOOOYQZ RLONMPOPXRYSYQZP[ RPOTMUNWOXO RSNTOVO RRNTPVPXO",
	3619: " 59JZMOMSOTUTWUWY RNONS RVUVY RPNOOOSQT RSTUUUYTZ RMOPNRMTNVNWM RQNSN RPNROTOVN RWYTZR[PZNZL[ RSZQZ RTZRYOYL[ RWMVOTROWL[",
	3620: " 28MWPHQJQXOYPYRZS[ RRJQHRGRYTZ RPHSFSXUYVYTZS[ RNMQM RSMVM",
	3621: " 47I[KOLOMPMXKY RLNNONYPZ RKOMMOOOXQYRY RKYLYNZO[PZRYUX RUMVNXOYOWPWXXYYY RTNVOVYWZ RUMSOUPUYW[YY",
	3622: " 36I[LMMOMXP[RYUXWX RMNNONXQZ RLMNNOOOWPXRY RUMVNXOYOWPWX RTNVOVW RUMSOUPUX",
	3623: " 57E_HMIOIXL[NYQX RINJOJXMZ RHMJNKOKWLXNY RQMOOQPQXT[VYYX[X RPNRORXUZ RQMRNTOSPSWTXVY RYMZN\\O]O[P[X RXNZOZW RYMWOYPYX",
	3624: " 59H[KOLONPOQSYTZV[XY RMNOOTYVZ RKOMMONPOTWUXWYXY RRSUMVNXNYM RUNVOWO RTOVPXOYM RQUN[MZKZJ[ RNZMYLY ROYMXKYJ[ RMTPT RSTVT",
	3625: " 60I[KOLOMPMXKY RLNNONYPZ RKOMMOOOXQYRY RKYLYNZO[PZRYUX RUMVNXOYOWPW\\V_TaRbQaO`M` RTNVOV\\ RSaQ`P` RUMSOUPUZV]V_ RTaS`Q_O_M`",
	3626: " 38I[XML[ RLONPQPTOXM RMNOOSO RLONMPNTNXM RL[PYSXVXXY RQYUYWZ RL[PZTZV[XY RNTVT",
	3700: " 42H\\LHLXJY RMIMXPZ RNHNXPYQZ RLHNHSGUF RSGTHVIVY RTGWIWX RUFVGXHZHXIXY RJYLYNZO[QZVYXY",
	3701: " 27H\\OHPIQKQXOY RQIPHQGRIRYTZ ROHRFSHSXUYVY ROYPYRZS[TZVY",
	3702: " 48H\\LHNHPGQFSGVHXH RPHRG RLHNIPIRHSG RVHVP RWIWO RXHXPQPNQLSKVK[ RK[OYSXVXZY RNZQYVYYZ RK[PZUZX[ZY",
	3703: " 57H\\LHMHOGPFRGVHXH ROHQG RLHNIPIRG RVHVO RWIWN RXHXOVOSPQQ RQPSQVRXRXY RWSWX RVRVY RKYMXOXQYRZ ROYQZ RKYMYOZP[RZVYXY",
	3704: " 41H\\UFKPKUTU RVUZU[V[TZU RLPLT RMNMU RTGTXRY RUJVHUGUYWZ RUFWHVJVXXYYY RRYSYUZV[WZYY",
	3705: " 53H\\LFLO RLFXF RMGVG RLHUHWGXF RVLUMSNOOLO RSNTNVOVY RUMWNWX RVLWMYNZNXOXY RKYMXOXQYRZ ROYQZ RKYMYOZP[RZVYXY",
	3706: " 59H\\LHLXJY RMIMXPZ RNHNXPYQZ RLHNHRGTFUGWHXH RSGUH RRGTIVIXH RNPOPSOUNVM RSOTOVPVY RUNWPWX RVMWNYOZOXPXY RJYLYNZO[QZVYXY",
	3707: " 38H\\KHMFPGUGZF RLGOHTHWG RKHOIRIVHZF RZFYHWKSOQRPUPXQ[ RRQQTQWRZ RUMSPRSRVSYQ[",
	3708: " 71H\\LILO RMJMN RNINO RLINISHUGVF RSHTHVIVO RUGWHWN RVFWGYHZHXIXO RLONOVRXR RXOVONRLR RLRLXJY RMSMXPZ RNRNXPYQZ RVRVY RWSWX RXRXY RJYLYNZO[QZVYXY",
	3709: " 60H\\LHLQJR RMIMROS RNHNQPRQR RLHNHSGUF RSGTHVIVY RTGWIWX RUFVGXHZHXIXY RJRKRMSNTOSQRUQVQ RKYMXOXQYRZ ROYQZ RKYMYOZP[RZVYXY",
	3710: " 11LXRXPZR[TZRX RRYQZSZRY",
	3711: " 14LXR^R\\PZRXSZS\\R^P_ RRYQZR[RY",
	3712: " 22LXRMPORPTORM RRNQOSORN RRXPZR[TZRX RRYQZSZRY",
	3713: " 25LXRMPORPTORM RRNQOSORN RR^R\\PZRXSZS\\R^P_ RRYQZR[RY",
	3714: " 30LXRFQGOHQIRT RRISHRGQHRIRT RRFSGUHSIRT RRXPZR[TZRX RRYQZSZRY",
	3715: " 51I[LJMHNGQFSFVGWHXJXLWNUPSQ RMJNH RVHWIWMVN RLJNKNIOGQF RSFUGVIVMUOSQ RRQRTSQQQRT RRXPZR[TZRX RRYQZSZRY",
	3716: " 14LXTFRGQIQKRMTKRIRG RRJRLSKRJ",
	3717: " 14LXRLRJPHRFSHSJRLPM RRGQHRIRG",
	3718: " 62E_YNZO[O\\N RXOYP[P RXPYQZQ[P\\N RYNST RRUL[HVNP ROOSKOFJLPRTXVZX[Z[[Z\\X RLZIV RRKOG RKLPQTWVYXZ[Z RMZIU RRLNG RKKQQUWVXXY[Y\\X",
	3719: " 60H\\PBP_ RTBT_ RTFVGWIWKYJXHWGTFPFMGKIKLLNOPURWSXUXXWZ RXJWH RLLMNOOUQWRXT RMYLW RMGLILKMMONUPXRYTYWXYWZT[P[MZLYKWMVMXNZP[",
	3720: "  8G^[BIbJb R[B\\BJb",
	3721: " 27KYUBSDQGOKNPNTOYQ]S`Ub RQHPKOOOUPYQ\\ RSDRFQIPOPUQ[R^S`",
	3722: " 27KYOBQDSGUKVPVTUYS]Q`Ob RSHTKUOUUTYS\\ RQDRFSITOTUS[R^Q`",
	3723: " 39JZRFQGSQRR RRFRR RRFSGQQRR RMINIVOWO RMIWO RMIMJWNWO RWIVINOMO RWIMO RWIWJMNMO",
	3724: "  8F_JQ[Q[R RJQJR[R",
	3725: " 16F_RIRZSZ RRISISZ RJQ[Q[R RJQJR[R",
	3726: " 16F_JM[M[N RJMJN[N RJU[U[V RJUJV[V",
	3727: " 11NWSFRGRM RSGRM RSFTGRM",
	3728: " 22I[NFMGMM RNGMM RNFOGMM RWFVGVM RWGVM RWFXGVM",
	3729: " 30KYQFOGNINKOMQNSNUMVKVIUGSFQF RQFNIOMSNVKUGQF RSFOGNKQNUMVISF",
	3801: " 52E_NHLIJKIMHPHSIUKV RJLIOISJU RNHLJKLJOJRKVKXJZH[ RVHXHXYVY RYHYY RZGZZ RHFKGQHVHZG\\F RJPXP RH[KZQYVYZZ\\[",
	3802: " 65E_LGLZ RMGMZ RPFNGNZP[ RHJJHLGPFUFXGZIZKYM RXHYIYKXM RUFWGXIXKWL RQUOTNRNPONPMSLVLYM[O\\Q\\T[WYYWZT[P[LZJYHW RZO[Q[UZW RVLYNZQZUYXWZ",
	3803: " 60E_\\F[HZJXHVGSFQFNGLHJJILHOHRIUJWLYNZQ[S[VZXYZW[Y\\[ R[HZMZT[Y RZKYJ RZNYKXIVG RJKINISJV RNGLIKKJNJSKVLXNZ RYWZV RVZXXYVZS",
	3804: " 46E_KGKZ RLGLZ RNFMGMZN[ RHKIIKGNFSFVGXHZJ[L\\O\\R[UZWXYVZS[N[KZIXHV RZK[N[SZV RVGXIYKZNZSYVXXVZ",
	3805: " 86E_\\F[HZJXHVGSFQFNGLHJJILHOHRIUJWLYNZQ[S[VZXYZW[Y\\[ R[HZMZT[Y RZKYJ RZMXIVG RJKINISJV RNGLIKKJNJSKVLXNZ RYWZV RVZXXYVZS RJPKONOUQXQZP RPPRQURWRYQ RMORRUSWSYRZP RZMYLXLWMXNYM",
	3806: " 69E_JHJZ RMGKHKY ROFMGLILYNY RHJJHLGOFSFVGXHYI\\F R\\F[HZLZO[S\\U RZIYK RVGXIYLZO RLPMOOOTPWPYO RQPTQVQXP RNOTRVRXQYOYLXKWKVLWMXL RH[JZNYSYYZ\\[",
	3807: " 90E_\\F[HZJXHVGSFQFNGLHJJILHOHRIUJWLYNZQ[T[VZXYYXZV[Y\\[ R[HZMZT[Y RZKYJ RZNYKXIVG RJKINISJV RNGLIKKJNJSKVLXNZ RXXYVYR RVZWYXVXQ RKSLRMSLTKTJS RJPKNMMOMRNUPWQ RKOMNONROTP RJPLOOOUQYQZP",
	3808: " 50E_JGJZH[ RKHKZ RNHLHLZ RHFJGNHSHYG\\F RLPMNOLRKVKYL[N\\Q\\T[UYV RZN[P[SZU RVKXLYMZOZSYVYXZZ\\[ RH[LZPZU[",
	3809: " 23E_QIQY RRJRX RSISY RHFLHPITIXH\\F RH[KZOYUYYZ\\[",
	3810: " 42E_TIVIVXUZS[ RWIWXVY RXHXY RHFLHPITIXH\\F RIOHQHUIXKZN[S[VZXYZW\\T RIUJXKY RHSJUKXLZN[",
	3811: " 70E_JGJZH[ RKHKZ RNHLHLZ RHFJGNHSHYG\\F RLPMNOLRKUKXLYMYOXPSRQSPTPUQVRUQT RWLXMXOWP RUKWMWOVPSR RSRVRYSZUZWYX RWSYUYW RSRVSXUYXZZ[[\\[ RH[LZPZU[",
	3812: " 45E_JGJZ RKHKY RNHLHLYNY R\\KZNYPXSXUYW[X RZOYRYUZW R\\K[MZQZT[X\\[ RHFJGNHSHYG\\F RH[JZNYSYYZ\\[",
	3813: " 68E_QIQY RRJRX RSISY RNYLWJVIUHRHMIJKHMGPFTFWGYH[J\\M\\R[UZVXWVY RJUIRIMJJ RLWKUJRJLKIMG RZJ[M[RZU RWGYIZLZRYUXW RHFLHPITIXH\\F RH[KZOYUYYZ\\[",
	3814: " 48E_JHJZH[ RLHKIKZ ROFMGLILZ RHJJHLGOFSFVGXHZJ[L\\O\\S[UYV RZK[N[RZU RVGXIYKZNZRYVYXZZ[[\\[ RH[LZPZU[",
	3815: " 54E_QFNGLHJJILHOHRIUJWLYNZQ[S[VZXYZW[U\\R\\O[LZJXHVGSFQF RJKINISJV RNGLIKKJNJSKVLXNZ RZV[S[NZK RVZXXYVZSZNYKXIVG",
	3816: " 51E_JIJZ RMHKJKY RQFOGMILKLYNY RHKJINGQFTFWGYH[J\\M\\O[RYTVURUOTMRLO RZJ[L[PZR RWGYIZLZPYSVU RH[JZNYSYYZ\\[",
	3817: " 74E_QFNGLHJJILHOHRIUJWLYNZQ[S[VZXYZW[U\\R\\O[LZJXHVGSFQF RJKINISJV RNGLIKKJNJSKVLXNZ RZV[S[NZK RVZXXYVZSZNYKXIVG RJSKUNVTW[W\\X\\Z[[[Z\\Y RPWRW RKUNWQXSXTW",
	3818: " 69E_JIJZH[ RKIKZ RLHLZ RHKJILHNGQFUFYG[I\\K\\N[PZQ RYHZI[K[NZP RUFWGYIZKZOYQ RXRUSRSPRPPROUOXPZR\\U\\W[XZX RXQYR[V[WZT RTOVPXRYTZX[Z\\[ RH[LZPZU[",
	3819: " 94E_TFZG\\F[H[JYHWGTFPFMGJJIMIOJRLTOURUTTUSVQVP R[GZH[J RJPKRLSOTRTTS RKIJKJNKPMRPSRSTRVPWOXO RLQMQNPPNRMUMWNYPZRZUYXWZ RPMRLULXMZO[R[UZW RIWJYIZ RNPNOOMPLRKUKXL[O\\R\\T[WYYWZT[P[MZKYIWIYH[JZP[",
	3820: " 66E_QHMHKIJJILHOHSIVJXKYMZP[S[VZXYZW[U\\R\\N[KYIWH RUHTITKULVKUJ RISJVLXNYQZTZWY RJJINIQJTLWNXQYTYWXYW[T\\R RHFKI RKHLG RIGJGKFMGQHWHZG\\F",
	3821: " 51E_LHJJILHOHRIUJWLYNZQ[U[XZZY RKJJLIOISJV RKILJLKKMJPJSKVLXNZ RVHXHXXWZU[ RYHYXXY RZGZY\\[ RHFKGQHVHZG\\F",
	3822: " 31E_HFR[ RIGJHQWRY RJGKHRWSX R\\FR[ RWNUS RYLUQTTTV RHFJGOHUHZG\\F",
	3823: " 67E_LHJJILHOHRIUJWLYNZQ[S[VZXYZW[U\\R\\O[LZJXH RJLIOIRJUKW RJJKKKLJOJRKVLXNZ RYWZU[R[OZL RVZXXYVZRZOYLYKZJ RQIQ[ RRJRZ RSIS[ RHFLHPITIXH\\F",
	3824: " 41E_HFXYYZ RIGKHZZ RLH\\[ R\\FSP RQRJZ RPSMULW RQRMTLUKWKY RHFLHPITIXH\\F RH[JZNYSYYZ\\[",
	3825: " 47E_XHXZ RYHYY RZGZY RKHIJHMHPISKUMVPWSWVVXU RLUOVUV RHPIRKTNUTUVV RHFLHPITIXH\\F RHWJYLZP[T[XZ\\X",
	3826: " 73E_HFIGKHNHSFVFYGZIZKYM RXGYIYKXM RVFWGXIXL RXNTOROPNPLRKTKXL RTKVLWMVNTO RYM[O\\R\\T[WYYWZT[P[MZKYIWHTHRIOJNLMNMPNPPOQNPOO RXMZO[Q[UZW RXNYOZQZUYXWZ",
	3901: " 42J[PQMTMXP[TY RNTNXPZ ROROWRZ RRSMNNMONNO RONSNUMWOWXXY RUNVOVXUYVZWYVX RSNUPUXTYV[XY",
	3902: " 31IZNHLFMJMXP[UYWX RNHNXPZ RNHPFOJOWRZ ROOTMWPWX RTNVPVX RRNUQUY",
	3903: " 23KWNPNYP[RY ROPOYPZ RPOPXQYRY RNPTMVOTPRN RSNUO",
	3904: " 32JZRMMPMXP[RZUYWY RNPNXPZ ROOOWRZ RPIPFQIWPWY RPIVPVX RPIMIPJUPUY",
	3905: " 25KXNPNYP[RY ROPOYPZ RPOPXQYRY RNPTMWQPU RSNVQ RRNUR",
	3906: " 32KWOIOXNYP[ RPIPXOYPZQYPX RQHQXRYP[ ROIUFWHUISG RTGVH RLMOM RQMUM",
	3907: " 41J[MPMXP[UY RNPNXPZ ROOOWRZ RMPOOTMWPW]V_U`SaQaO`MaObQa RTNVPV]U_ RPaNa RRNUQU^T`Sa",
	3908: " 42I[NHLFMJMXLYN[ RNHNXMYNZOYNX RNHPFOJOXPYN[ ROORNTMWPWYT]T`UbVbT` RTNVPVYU[ RRNUQUZT]",
	3909: " 37MWRFPHRJTHRF RRGQHRISHRG RRMPOQPQXPYR[ RRPSORNQORPRXQYRZSYRX RRMTOSPSXTYR[",
	3910: " 37MWRFPHRJTHRF RRGQHRISHRG RRMPOQPQYT] RRPSORNQORPRYS[ RRMTOSPSZT]T`RbPaPbRb",
	3911: " 51IZNHLFMJMXLYN[ RNHNXMYNZOYNX RNHPFOJOXPYN[ ROPRNTMVPSROU RSNUP RRNTQ RRSSTTYV[XY RSSTUUYVZ RSRTSVXWYXY",
	3912: " 21MWRHPFQJQXPYR[ RRHRXQYRZSYRX RRHTFSJSXTYR[",
	3913: " 66E_GOHOIPIXHYJ[ RINJOJXIYJZKYJX RGOIMKOKXLYJ[ RKONNPMSOSXTYR[ RPNRORXQYRZSYRX RNNQPQXPYR[ RSOVNXM[O[X\\YZ[ RXNZOZXYYZZ[YZX RVNYPYXXYZ[",
	3914: " 44I[KOLOMPMXLYN[ RMNNONXMYNZOYNX RKOMMOOOXPYN[ ROORNTMWOWXXYV[ RTNVOVXUYVZWYVX RRNUPUXTYV[",
	3915: " 28JZMPMXP[UYWX RNPNXPZ ROOOWRZ RMPOOTMWPWX RTNVPVX RRNUQUY",
	3916: " 47IZLMMOMXKYMYM_LbN` RNON` RLMNNOOOXQYRZ RNYOYQZ ROZP[UYWX ROZO_PbN` ROORNTMWPWX RTNVPVX RRNUQUY",
	3917: " 31J[MPMXP[UY RNPNXPZ ROOOWRZ RMPOOTMWPW_XbV` RTNVPV` RRNUQU_TbV`",
	3918: " 31KXMONOOPOXNYP[ RONPOPXOYPZQYPX RMOOMQOQXRYP[ RQOUMWOUPSN RTNVO",
	3919: " 41JZMPMSOUURWTWX RNPNSOT ROOOSPT RUSVTVX RTSUTUY RMPSMVNTOQN RRNUN RWXQ[MYOXSZ ROYQZ",
	3920: " 27MWRHPFQJQXPYR[ RRHRXQYRZSYRX RRHTFSJSXTYR[ RNMQM RSMVM",
	3921: " 40I[KOLOMPMYP[UY RMNNONYPZ RKOMMOOOXRZ RVMXOWPWXXYYY RVPWOVNUOVPVYWZ RVMTOUPUYW[YY",
	3922: " 36I[LMMOMXQ[SYWW RMNNONXQZ RLMNNOOOWRYSY RVMXOWPWW RVPWOVNUOVPVW RVMTOUPUX",
	3923: " 59E_HMIOIXM[OYQX RINJOJXMZ RHMJNKOKWNYOY RRMPOQPQXU[WY[W RRPSORNQORPRXUZ RRMTOSPSWVYWY RZM\\O[P[W RZP[OZNYOZPZW RZMXOYPYX",
	3924: " 39I[LONPUZV[XY RMNOOUYWZ RLONMONVXXY RXMVMVOXOXMVOSS RQUNYL[N[NYLYL[ RNTQT RSTVT",
	3925: " 49I[KOLOMPMYP[UY RMNNONYPZ RKOMMOOOXRZ RVMXOWPW]V_U`SaQaO`MaObQa RVPWOVNUOVPV^U_ RPaNa RVMTOUPU^T`Sa",
	3926: " 43L[RNOPOORNTMWOWSRU RTNVOVS RRNUPUSTT RRUWWW]V_U`SaQaO`MaObQa RVWV^U_ RPaNa RTVUWU^T`Sa"
}, U = {
	"\\frac": {
		glyph: 0,
		arity: 2,
		flags: {}
	},
	"\\binom": {
		glyph: 0,
		arity: 2,
		flags: {}
	},
	"\\sqrt": {
		glyph: 2267,
		arity: 1,
		flags: {
			opt: !0,
			xfl: !0,
			yfl: !0
		}
	},
	"^": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	_: {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"(": {
		glyph: 2221,
		arity: 0,
		flags: { yfl: !0 }
	},
	")": {
		glyph: 2222,
		arity: 0,
		flags: { yfl: !0 }
	},
	"[": {
		glyph: 2223,
		arity: 0,
		flags: { yfl: !0 }
	},
	"]": {
		glyph: 2224,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\langle": {
		glyph: 2227,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\rangle": {
		glyph: 2228,
		arity: 0,
		flags: { yfl: !0 }
	},
	"|": {
		glyph: 2229,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\|": {
		glyph: 2230,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\{": {
		glyph: 2225,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\}": {
		glyph: 2226,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\#": {
		glyph: 2275,
		arity: 0,
		flags: {}
	},
	"\\$": {
		glyph: 2274,
		arity: 0,
		flags: {}
	},
	"\\&": {
		glyph: 2273,
		arity: 0,
		flags: {}
	},
	"\\%": {
		glyph: 2271,
		arity: 0,
		flags: {}
	},
	"\\begin": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\end": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\left": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\right": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\middle": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\cdot": {
		glyph: 2236,
		arity: 0,
		flags: {}
	},
	"\\pm": {
		glyph: 2233,
		arity: 0,
		flags: {}
	},
	"\\mp": {
		glyph: 2234,
		arity: 0,
		flags: {}
	},
	"\\times": {
		glyph: 2235,
		arity: 0,
		flags: {}
	},
	"\\div": {
		glyph: 2237,
		arity: 0,
		flags: {}
	},
	"\\leqq": {
		glyph: 2243,
		arity: 0,
		flags: {}
	},
	"\\geqq": {
		glyph: 2244,
		arity: 0,
		flags: {}
	},
	"\\leq": {
		glyph: 2243,
		arity: 0,
		flags: {}
	},
	"\\geq": {
		glyph: 2244,
		arity: 0,
		flags: {}
	},
	"\\propto": {
		glyph: 2245,
		arity: 0,
		flags: {}
	},
	"\\sim": {
		glyph: 2246,
		arity: 0,
		flags: {}
	},
	"\\equiv": {
		glyph: 2240,
		arity: 0,
		flags: {}
	},
	"\\dagger": {
		glyph: 2277,
		arity: 0,
		flags: {}
	},
	"\\ddagger": {
		glyph: 2278,
		arity: 0,
		flags: {}
	},
	"\\ell": {
		glyph: 662,
		arity: 0,
		flags: {}
	},
	"\\vec": {
		glyph: 2261,
		arity: 1,
		flags: {
			hat: !0,
			xfl: !0,
			yfl: !0
		}
	},
	"\\overrightarrow": {
		glyph: 2261,
		arity: 1,
		flags: {
			hat: !0,
			xfl: !0,
			yfl: !0
		}
	},
	"\\overleftarrow": {
		glyph: 2263,
		arity: 1,
		flags: {
			hat: !0,
			xfl: !0,
			yfl: !0
		}
	},
	"\\bar": {
		glyph: 2231,
		arity: 1,
		flags: {
			hat: !0,
			xfl: !0
		}
	},
	"\\overline": {
		glyph: 2231,
		arity: 1,
		flags: {
			hat: !0,
			xfl: !0
		}
	},
	"\\widehat": {
		glyph: 2247,
		arity: 1,
		flags: {
			hat: !0,
			xfl: !0,
			yfl: !0
		}
	},
	"\\hat": {
		glyph: 2247,
		arity: 1,
		flags: { hat: !0 }
	},
	"\\acute": {
		glyph: 2248,
		arity: 1,
		flags: { hat: !0 }
	},
	"\\grave": {
		glyph: 2249,
		arity: 1,
		flags: { hat: !0 }
	},
	"\\breve": {
		glyph: 2250,
		arity: 1,
		flags: { hat: !0 }
	},
	"\\tilde": {
		glyph: 2246,
		arity: 1,
		flags: { hat: !0 }
	},
	"\\underline": {
		glyph: 2231,
		arity: 1,
		flags: {
			mat: !0,
			xfl: !0
		}
	},
	"\\not": {
		glyph: 2220,
		arity: 1,
		flags: {}
	},
	"\\neq": {
		glyph: 2239,
		arity: 1,
		flags: {}
	},
	"\\ne": {
		glyph: 2239,
		arity: 1,
		flags: {}
	},
	"\\exists": {
		glyph: 2279,
		arity: 0,
		flags: {}
	},
	"\\in": {
		glyph: 2260,
		arity: 0,
		flags: {}
	},
	"\\subset": {
		glyph: 2256,
		arity: 0,
		flags: {}
	},
	"\\supset": {
		glyph: 2258,
		arity: 0,
		flags: {}
	},
	"\\cup": {
		glyph: 2257,
		arity: 0,
		flags: {}
	},
	"\\cap": {
		glyph: 2259,
		arity: 0,
		flags: {}
	},
	"\\infty": {
		glyph: 2270,
		arity: 0,
		flags: {}
	},
	"\\partial": {
		glyph: 2265,
		arity: 0,
		flags: {}
	},
	"\\nabla": {
		glyph: 2266,
		arity: 0,
		flags: {}
	},
	"\\aleph": {
		glyph: 2077,
		arity: 0,
		flags: {}
	},
	"\\wp": {
		glyph: 2190,
		arity: 0,
		flags: {}
	},
	"\\therefore": {
		glyph: 740,
		arity: 0,
		flags: {}
	},
	"\\mid": {
		glyph: 2229,
		arity: 0,
		flags: {}
	},
	"\\sum": {
		glyph: 2402,
		arity: 0,
		flags: { big: !0 }
	},
	"\\prod": {
		glyph: 2401,
		arity: 0,
		flags: { big: !0 }
	},
	"\\bigoplus": {
		glyph: 2284,
		arity: 0,
		flags: { big: !0 }
	},
	"\\bigodot": {
		glyph: 2281,
		arity: 0,
		flags: { big: !0 }
	},
	"\\int": {
		glyph: 2412,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\oint": {
		glyph: 2269,
		arity: 0,
		flags: { yfl: !0 }
	},
	"\\oplus": {
		glyph: 1284,
		arity: 0,
		flags: {}
	},
	"\\odot": {
		glyph: 1281,
		arity: 0,
		flags: {}
	},
	"\\perp": {
		glyph: 738,
		arity: 0,
		flags: {}
	},
	"\\angle": {
		glyph: 739,
		arity: 0,
		flags: {}
	},
	"\\triangle": {
		glyph: 842,
		arity: 0,
		flags: {}
	},
	"\\Box": {
		glyph: 841,
		arity: 0,
		flags: {}
	},
	"\\rightarrow": {
		glyph: 2261,
		arity: 0,
		flags: {}
	},
	"\\to": {
		glyph: 2261,
		arity: 0,
		flags: {}
	},
	"\\leftarrow": {
		glyph: 2263,
		arity: 0,
		flags: {}
	},
	"\\gets": {
		glyph: 2263,
		arity: 0,
		flags: {}
	},
	"\\circ": {
		glyph: 902,
		arity: 0,
		flags: {}
	},
	"\\bigcirc": {
		glyph: 904,
		arity: 0,
		flags: {}
	},
	"\\bullet": {
		glyph: 828,
		arity: 0,
		flags: {}
	},
	"\\star": {
		glyph: 856,
		arity: 0,
		flags: {}
	},
	"\\diamond": {
		glyph: 743,
		arity: 0,
		flags: {}
	},
	"\\ast": {
		glyph: 728,
		arity: 0,
		flags: {}
	},
	"\\log": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\ln": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\exp": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\mod": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\lim": {
		glyph: 0,
		arity: 0,
		flags: {
			txt: !0,
			big: !0
		}
	},
	"\\sin": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\cos": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\tan": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\csc": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\sec": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\cot": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\sinh": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\cosh": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\tanh": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\csch": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\sech": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\coth": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\arcsin": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\arccos": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\arctan": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\arccsc": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\arcsec": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\arccot": {
		glyph: 0,
		arity: 0,
		flags: { txt: !0 }
	},
	"\\text": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathnormal": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathrm": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathit": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathbf": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathsf": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathtt": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathfrak": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathcal": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathbb": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\mathscr": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\rm": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\it": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\bf": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\sf": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\tt": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\frak": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\cal": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\bb": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\scr": {
		glyph: 0,
		arity: 1,
		flags: {}
	},
	"\\quad": {
		glyph: 0,
		arity: 0,
		flags: {}
	},
	"\\,": {
		glyph: 0,
		arity: 0,
		flags: {}
	},
	"\\.": {
		glyph: 0,
		arity: 0,
		flags: {}
	},
	"\\;": {
		glyph: 0,
		arity: 0,
		flags: {}
	},
	"\\!": {
		glyph: 0,
		arity: 0,
		flags: {}
	},
	"\\alpha": {
		glyph: 2127,
		flags: {}
	},
	"\\beta": {
		glyph: 2128,
		flags: {}
	},
	"\\gamma": {
		glyph: 2129,
		flags: {}
	},
	"\\delta": {
		glyph: 2130,
		flags: {}
	},
	"\\varepsilon": {
		glyph: 2131,
		flags: {}
	},
	"\\zeta": {
		glyph: 2132,
		flags: {}
	},
	"\\eta": {
		glyph: 2133,
		flags: {}
	},
	"\\vartheta": {
		glyph: 2134,
		flags: {}
	},
	"\\iota": {
		glyph: 2135,
		flags: {}
	},
	"\\kappa": {
		glyph: 2136,
		flags: {}
	},
	"\\lambda": {
		glyph: 2137,
		flags: {}
	},
	"\\mu": {
		glyph: 2138,
		flags: {}
	},
	"\\nu": {
		glyph: 2139,
		flags: {}
	},
	"\\xi": {
		glyph: 2140,
		flags: {}
	},
	"\\omicron": {
		glyph: 2141,
		flags: {}
	},
	"\\pi": {
		glyph: 2142,
		flags: {}
	},
	"\\rho": {
		glyph: 2143,
		flags: {}
	},
	"\\sigma": {
		glyph: 2144,
		flags: {}
	},
	"\\tau": {
		glyph: 2145,
		flags: {}
	},
	"\\upsilon": {
		glyph: 2146,
		flags: {}
	},
	"\\varphi": {
		glyph: 2147,
		flags: {}
	},
	"\\chi": {
		glyph: 2148,
		flags: {}
	},
	"\\psi": {
		glyph: 2149,
		flags: {}
	},
	"\\omega": {
		glyph: 2150,
		flags: {}
	},
	"\\epsilon": {
		glyph: 2184,
		flags: {}
	},
	"\\theta": {
		glyph: 2185,
		flags: {}
	},
	"\\phi": {
		glyph: 2186,
		flags: {}
	},
	"\\varsigma": {
		glyph: 2187,
		flags: {}
	},
	"\\Alpha": {
		glyph: 2027,
		flags: {}
	},
	"\\Beta": {
		glyph: 2028,
		flags: {}
	},
	"\\Gamma": {
		glyph: 2029,
		flags: {}
	},
	"\\Delta": {
		glyph: 2030,
		flags: {}
	},
	"\\Epsilon": {
		glyph: 2031,
		flags: {}
	},
	"\\Zeta": {
		glyph: 2032,
		flags: {}
	},
	"\\Eta": {
		glyph: 2033,
		flags: {}
	},
	"\\Theta": {
		glyph: 2034,
		flags: {}
	},
	"\\Iota": {
		glyph: 2035,
		flags: {}
	},
	"\\Kappa": {
		glyph: 2036,
		flags: {}
	},
	"\\Lambda": {
		glyph: 2037,
		flags: {}
	},
	"\\Mu": {
		glyph: 2038,
		flags: {}
	},
	"\\Nu": {
		glyph: 2039,
		flags: {}
	},
	"\\Xi": {
		glyph: 2040,
		flags: {}
	},
	"\\Omicron": {
		glyph: 2041,
		flags: {}
	},
	"\\Pi": {
		glyph: 2042,
		flags: {}
	},
	"\\Rho": {
		glyph: 2043,
		flags: {}
	},
	"\\Sigma": {
		glyph: 2044,
		flags: {}
	},
	"\\Tau": {
		glyph: 2045,
		flags: {}
	},
	"\\Upsilon": {
		glyph: 2046,
		flags: {}
	},
	"\\Phi": {
		glyph: 2047,
		flags: {}
	},
	"\\Chi": {
		glyph: 2048,
		flags: {}
	},
	"\\Psi": {
		glyph: 2049,
		flags: {}
	},
	"\\Omega": {
		glyph: 2050,
		flags: {}
	}
};
function Qe(e, t = "math") {
	let n = e.charCodeAt(0);
	if (65 <= n && n <= 90) {
		let e = n - 65;
		return t == "text" || t == "rm" ? e + 2001 : t == "tt" ? e + 501 : t == "bf" || t == "bb" ? e + 3001 : t == "sf" ? e + 2501 : t == "frak" ? e + 3301 : t == "scr" || t == "cal" ? e + 2551 : e + 2051;
	}
	if (97 <= n && n <= 122) {
		let e = n - 97;
		return t == "text" || t == "rm" ? e + 2101 : t == "tt" ? e + 601 : t == "bf" || t == "bb" ? e + 3101 : t == "sf" ? e + 2601 : t == "frak" ? e + 3401 : t == "scr" || t == "cal" ? e + 2651 : e + 2151;
	}
	if (48 <= n && n <= 57) {
		let e = n - 48;
		return t == "it" ? e + 2750 : t == "bf" ? e + 3200 : t == "tt" ? e + 700 : e + 2200;
	}
	return {
		".": 2210,
		",": 2211,
		":": 2212,
		";": 2213,
		"!": 2214,
		"?": 2215,
		"'": 2216,
		"\"": 2217,
		"*": 2219,
		"/": 2220,
		"-": 2231,
		"+": 2232,
		"=": 2238,
		"<": 2241,
		">": 2242,
		"~": 2246,
		"@": 2273,
		"\\": 804
	}[e];
}
//#endregion
//#region src/editor/core/draw/particle/latex/utils/LaTexUtils.ts
var $e = {
	SUB_SUP_SCALE: .5,
	SQRT_MAG_SCALE: .5,
	FRAC_SCALE: .85,
	LINE_SPACING: .5,
	FRAC_SPACING: .4
};
function et(e) {
	e = e.replace(/\n/g, " ");
	let t = 0, n = [], r = "";
	for (; t < e.length;) e[t] == " " ? r.length && (n.push(r), r = "") : e[t] == "\\" ? r.length == 1 && r[0] == "\\" ? (r += e[t], n.push(r), r = "") : (r.length && n.push(r), r = e[t]) : /[A-Za-z0-9\.]/.test(e[t]) ? r += e[t] : (r.length && r != "\\" && (n.push(r), r = ""), r += e[t], n.push(r), r = ""), t++;
	return r.length && n.push(r), n;
}
function tt(e) {
	return {
		type: U[e] ? "symb" : "char",
		mode: "math",
		text: e,
		chld: [],
		bbox: null
	};
}
function nt(e) {
	let t = 0, n = {
		type: "node",
		text: "",
		mode: "math",
		chld: [],
		bbox: null
	};
	function r() {
		if (e[t] != "[") return null;
		let n = 0, r = t;
		for (; r < e.length;) {
			if (e[r] == "[") n++;
			else if (e[r] == "]" && (n--, !n)) break;
			r++;
		}
		let i = nt(e.slice(t + 1, r));
		return t = r, i;
	}
	function i(n) {
		let r = t, i = r, a = 0, o = 0, s = [];
		for (; r < e.length;) {
			if (e[r] == "{") a || (i = r), a++;
			else if (e[r] == "}") {
				if (a--, !a && (s.push(nt(e.slice(i + 1, r))), o++, o == n)) break;
			} else if (a == 0 && (s.push(tt(e[r])), o++, o == n)) break;
			r++;
		}
		return t = r, s;
	}
	for (t = 0; t < e.length; t++) {
		let a = U[e[t]], o = {
			type: "",
			text: e[t],
			mode: "math",
			chld: [],
			bbox: null
		};
		if (a) {
			if (a.arity) {
				t++, o.type = "func";
				let e = null;
				a.flags.opt && (e = r(), e && t++), o.chld = i(a.arity), e && o.chld.push(e);
			} else o.type = "symb";
		} else e[t] == "{" ? (o.type = "node", o.text = "", o.chld = i(1)) : o.type = "char";
		n.chld.push(o);
	}
	return n.chld.length == 1 && (n = n.chld[0]), n;
}
function rt(e) {
	let t = 0;
	for (; t < e.length;) {
		if (e[t].text == "\\begin") {
			let n;
			for (n = t; n < e.length && e[n].text != "\\end"; n++);
			let r = e.splice(t + 1, n - (t + 1));
			rt(r), e[t].text = e[t].chld[0].text, e[t].chld = r, e.splice(t + 1, 1);
		}
		t++;
	}
}
function it(e, t, n, r, i, a) {
	if (n ??= t, e.bbox) {
		a && (e.bbox.x *= t, e.bbox.y *= n), e.bbox.w *= t, e.bbox.h *= n;
		for (let r = 0; r < e.chld.length; r++) it(e.chld[r], t, n, 0, 0, !0);
		e.bbox.x += r, e.bbox.y += i;
	}
}
function at(e) {
	let t = Infinity, n = -Infinity, r = Infinity, i = -Infinity;
	for (let a = 0; a < e.length; a++) e[a].bbox && (t = Math.min(t, e[a].bbox.x), r = Math.min(r, e[a].bbox.y), n = Math.max(n, e[a].bbox.x + e[a].bbox.w), i = Math.max(i, e[a].bbox.y + e[a].bbox.h));
	return {
		x: t,
		y: r,
		w: n - t,
		h: i - r
	};
}
function ot(e) {
	if (!e.length) return null;
	let t = at(e);
	for (let n = 0; n < e.length; n++) e[n].bbox && (e[n].bbox.x -= t.x, e[n].bbox.y -= t.y);
	return {
		type: "node",
		text: "",
		mode: "math",
		chld: e,
		bbox: t
	};
}
function st(e, t = "center") {
	for (let t = 0; t < e.length; t++) if (e[t].text == "^" || e[t].text == "'") {
		let n = 0, r = t;
		for (; r > 0 && (e[r].text == "^" || e[r].text == "_" || e[r].text == "'");) r--;
		n = e[r].bbox.y, e[t].text == "'" ? e[t].bbox.y = n : (it(e[t], $e.SUB_SUP_SCALE, null, 0, 0), U[e[r].text] && U[e[r].text].flags.big ? e[t].bbox.y = n - e[t].bbox.h : e[r].text == "\\int" ? e[t].bbox.y = n : e[t].bbox.y = n - e[t].bbox.h / 2);
	} else if (e[t].text == "_") {
		let n = 1, r = t;
		for (; r > 0 && (e[r].text == "^" || e[r].text == "_" || e[r].text == "'");) r--;
		n = e[r].bbox.y + e[r].bbox.h, it(e[t], $e.SUB_SUP_SCALE, null, 0, 0), U[e[r].text] && U[e[r].text].flags.big ? e[t].bbox.y = n : e[r].text == "\\int" ? e[t].bbox.y = n - e[t].bbox.h : e[t].bbox.y = n - e[t].bbox.h / 2;
	}
	function n(t, n, r, i, a) {
		let o = t, s = a, c = Infinity, l = -Infinity;
		for (; i > 0 ? o < e.length : o >= 0;) {
			if (e[o].text == n) s++;
			else if (e[o].text == r) {
				if (s--, s == 0) break;
			} else e[o].text == "^" || e[o].text == "_" || e[o].bbox && (c = Math.min(c, e[o].bbox.y), l = Math.max(l, e[o].bbox.y + e[o].bbox.h));
			o += i;
		}
		return [c, l];
	}
	for (let t = 0; t < e.length; t++) if (e[t].text == "\\left") {
		let [r, i] = n(t, "\\left", "\\right", 1, 0);
		r != Infinity && i != -Infinity && (e[t].bbox.y = r, it(e[t], 1, (i - r) / e[t].bbox.h, 0, 0));
	} else if (e[t].text == "\\right") {
		let [r, i] = n(t, "\\right", "\\left", -1, 0);
		r != Infinity && i != -Infinity && (e[t].bbox.y = r, it(e[t], 1, (i - r) / e[t].bbox.h, 0, 0));
	} else if (e[t].text == "\\middle") {
		let [r, i] = n(t, "\\right", "\\left", -1, 1), [a, o] = n(t, "\\left", "\\right", 1, 1), s = Math.min(r, a), c = Math.max(i, o);
		s != Infinity && c != -Infinity && (e[t].bbox.y = s, it(e[t], 1, (c - s) / e[t].bbox.h, 0, 0));
	}
	if (!e.some((e) => e.text == "&" || e.text == "\\\\")) return;
	let r = [], i = [], a = [];
	for (let t = 0; t < e.length; t++) e[t].text == "&" ? (i.push(a), a = []) : e[t].text == "\\\\" ? (a.length && (i.push(a), a = []), r.push(i), i = []) : a.push(e[t]);
	a.length && i.push(a), i.length && r.push(i);
	let o = [], s = [];
	for (let e = 0; e < r.length; e++) {
		let t = [];
		for (let n = 0; n < r[e].length; n++) {
			let i = ot(r[e][n]);
			i && (o[n] = o[n] || 0, o[n] = Math.max(i.bbox.w + 1, o[n])), t[n] = i;
		}
		s.push(t);
	}
	let c = [];
	for (let e = 0; e < s.length; e++) {
		let t = Infinity, n = -Infinity;
		for (let r = 0; r < s[e].length; r++) s[e][r] && (t = Math.min(t, s[e][r].bbox.y), n = Math.max(n, s[e][r].bbox.y + s[e][r].bbox.h));
		c.push([t, n]);
	}
	for (let e = 0; e < c.length; e++) (c[e][0] == Infinity || c[e][1] == Infinity) && (c[e][0] = e == 0 ? 0 : c[e - 1][1], c[e][1] = c[e][0] + 2);
	for (let e = 1; e < s.length; e++) {
		let t = c[e - 1][1] - c[e][0] + $e.LINE_SPACING;
		for (let n = 0; n < s[e].length; n++) s[e][n] && (s[e][n].bbox.y += t);
		c[e][0] += t, c[e][1] += t;
	}
	e.splice(0, e.length);
	for (let n = 0; n < s.length; n++) {
		let r = 0;
		for (let i = 0; i < s[n].length; i++) {
			let a = s[n][i];
			if (!a) {
				r += o[i];
				continue;
			}
			a.bbox.x += r, r += o[i] - a.bbox.w, t == "center" ? a.bbox.x += (o[i] - a.bbox.w) / 2 : t == "left" || (t == "right" || t == "equation" && i != s[n].length - 1) && (a.bbox.x += o[i] - a.bbox.w), e.push(a);
		}
	}
}
function ct(e, t = "math") {
	let n = {
		"\\text": "text",
		"\\mathnormal": "math",
		"\\mathrm": "rm",
		"\\mathit": "it",
		"\\mathbf": "bf",
		"\\mathsf": "sf",
		"\\mathtt": "tt",
		"\\mathfrak": "frak",
		"\\mathcal": "cal",
		"\\mathbb": "bb",
		"\\mathscr": "scr",
		"\\rm": "rm",
		"\\it": "it",
		"\\bf": "bf",
		"\\sf": "tt",
		"\\tt": "tt",
		"\\frak": "frak",
		"\\cal": "cal",
		"\\bb": "bb",
		"\\scr": "scr"
	}[e.text] ?? t;
	if (!e.chld.length) {
		if (U[e.text]) {
			if (U[e.text].flags.big) e.bbox = e.text == "\\lim" ? {
				x: 0,
				y: 0,
				w: 3.5,
				h: 2
			} : {
				x: 0,
				y: -.5,
				w: 3,
				h: 3
			};
			else if (U[e.text].flags.txt) {
				let t = 0;
				for (let n = 1; n < e.text.length; n++) t += Je(Qe(e.text[n], "text")).w;
				t /= 16, e.bbox = {
					x: 0,
					y: 0,
					w: t,
					h: 2
				};
			} else if (U[e.text].glyph) {
				let t = Je(U[e.text].glyph).w;
				t /= 16, e.bbox = e.text == "\\int" || e.text == "\\oint" ? {
					x: 0,
					y: -1.5,
					w: t,
					h: 5
				} : {
					x: 0,
					y: 0,
					w: t,
					h: 2
				};
			} else e.bbox = {
				x: 0,
				y: 0,
				w: 1,
				h: 2
			};
		} else {
			let t = 0;
			for (let r = 0; r < e.text.length; r++) Je(Qe(e.text[r], n)) && (t += n == "tt" ? 16 : Je(Qe(e.text[r], n)).w);
			t /= 16, e.bbox = {
				x: 0,
				y: 0,
				w: t,
				h: 2
			};
		}
		e.mode = n;
		return;
	}
	if (e.text == "\\frac") {
		let t = e.chld[0], n = e.chld[1], r = $e.FRAC_SCALE;
		ct(t), ct(n), t.bbox.x = 0, t.bbox.y = 0, n.bbox.x = 0, n.bbox.y = 0;
		let i = Math.max(t.bbox.w, n.bbox.w) * r;
		it(t, r, null, (i - t.bbox.w * r) / 2, 0), it(n, r, null, (i - n.bbox.w * r) / 2, t.bbox.h + $e.FRAC_SPACING), e.bbox = {
			x: 0,
			y: -t.bbox.h + 1 - $e.FRAC_SPACING / 2,
			w: i,
			h: t.bbox.h + n.bbox.h + $e.FRAC_SPACING
		};
	} else if (e.text == "\\binom") {
		let t = e.chld[0], n = e.chld[1];
		ct(t), ct(n), t.bbox.x = 0, t.bbox.y = 0, n.bbox.x = 0, n.bbox.y = 0;
		let r = Math.max(t.bbox.w, n.bbox.w);
		it(t, 1, null, (r - t.bbox.w) / 2 + 1, 0), it(n, 1, null, (r - n.bbox.w) / 2 + 1, t.bbox.h), e.bbox = {
			x: 0,
			y: -t.bbox.h + 1,
			w: r + 2,
			h: t.bbox.h + n.bbox.h
		};
	} else if (e.text == "\\sqrt") {
		let t = e.chld[0];
		ct(t);
		let n = e.chld[1], r = 0;
		n && (ct(n), r = Math.max(n.bbox.w * $e.SQRT_MAG_SCALE - .5, 0), it(n, $e.SQRT_MAG_SCALE, null, 0, .5)), it(t, 1, null, 1 + r, .5), e.bbox = {
			x: 0,
			y: 2 - t.bbox.h - .5,
			w: t.bbox.w + 1 + r,
			h: t.bbox.h + .5
		};
	} else if (U[e.text] && U[e.text].flags.hat) {
		let t = e.chld[0];
		ct(t);
		let n = t.bbox.y - .5;
		t.bbox.y = .5, e.bbox = {
			x: 0,
			y: n,
			w: t.bbox.w,
			h: t.bbox.h + .5
		};
	} else if (U[e.text] && U[e.text].flags.mat) {
		let t = e.chld[0];
		ct(t), e.bbox = {
			x: 0,
			y: 0,
			w: t.bbox.w,
			h: t.bbox.h + .5
		};
	} else {
		let r = 0, i = 0, a = 1;
		for (let o = 0; o < e.chld.length; o++) {
			let s = e.chld[o], c = {
				"\\quad": 2,
				"\\,": 6 / 18,
				"\\:": 8 / 18,
				"\\;": 10 / 18,
				"\\!": -6 / 18
			}[s.text] ?? null;
			if (s.text == "\\\\") {
				i += a, r = 0, a = 1;
				continue;
			}
			if (s.text != "&") {
				if (c != null) {
					r += c;
					continue;
				}
				if (ct(s, n), it(s, 1, null, r, i), s.text == "^" || s.text == "_" || s.text == "'") {
					let t = o;
					for (; t > 0 && (e.chld[t].text == "^" || e.chld[t].text == "_" || e.chld[t].text == "'");) t--;
					let n = U[e.chld[t].text] && U[e.chld[t].text].flags.big;
					if (s.text == "'") {
						let n = t + 1, i = 0;
						for (; n < o;) e.chld[n].text == "'" && i++, n++;
						s.bbox.x = e.chld[t].bbox.x + e.chld[t].bbox.w + s.bbox.w * i, r = Math.max(r, s.bbox.x + s.bbox.w);
					} else if (n) {
						let n = e.chld[t].bbox.x + (e.chld[t].bbox.w - s.bbox.w * $e.SUB_SUP_SCALE) / 2;
						s.bbox.x = n, r = Math.max(r, e.chld[t].bbox.x + e.chld[t].bbox.w + (s.bbox.w * $e.SUB_SUP_SCALE - e.chld[t].bbox.w) / 2);
					} else s.bbox.x = e.chld[t].bbox.x + e.chld[t].bbox.w, r = Math.max(r, s.bbox.x + s.bbox.w * $e.SUB_SUP_SCALE);
				} else r += s.bbox.w;
				t == "text" && (r += 1), a = Math.max(s.bbox.y + s.bbox.h - i, a);
			}
		}
		i += a;
		let o = {
			bmatrix: ["[", "]"],
			pmatrix: ["(", ")"],
			Bmatrix: ["\\{", "\\}"],
			cases: ["\\{"]
		}, s = {
			bmatrix: "center",
			pmatrix: "center",
			Bmatrix: "center",
			cases: "left",
			matrix: "center",
			aligned: "equation"
		}[e.text] ?? "left", c = !!o[e.text], l = !!o[e.text] && o[e.text].length > 1;
		st(e.chld, s);
		let u = at(e.chld);
		e.text == "\\text" && (--u.x, u.w += 2);
		for (let t = 0; t < e.chld.length; t++) it(e.chld[t], 1, null, -u.x + (c ? 1.5 : 0), -u.y);
		e.bbox = {
			x: 0,
			y: 0,
			w: u.w + 1.5 * Number(c) + 1.5 * Number(l),
			h: u.h
		}, c && e.chld.unshift({
			type: "symb",
			text: o[e.text][0],
			mode: e.mode,
			chld: [],
			bbox: {
				x: 0,
				y: 0,
				w: 1,
				h: u.h
			}
		}), l && e.chld.push({
			type: "symb",
			text: o[e.text][1],
			mode: e.mode,
			chld: [],
			bbox: {
				x: u.w + 2,
				y: 0,
				w: 1,
				h: u.h
			}
		}), (c || l || e.text == "matrix") && (e.type = "node", e.text = "", e.bbox.y -= (e.bbox.h - 2) / 2);
	}
}
function lt(e) {
	function t(e, n, r) {
		let i = [];
		if (e.bbox) {
			if (n += e.bbox.x, r += e.bbox.y, e.text == "\\frac") {
				let t = e.chld[1].bbox.y - (e.chld[0].bbox.y + e.chld[0].bbox.h), a = {
					type: "symb",
					mode: e.mode,
					text: "\\bar",
					bbox: {
						x: n,
						y: r + (e.chld[1].bbox.y - t / 2) - t / 2,
						w: e.bbox.w,
						h: t
					},
					chld: []
				};
				i.push(a);
			} else if (e.text == "\\sqrt") {
				let t = e.chld[0].bbox.y, a = Math.max(0, e.chld[0].bbox.x - e.chld[0].bbox.h / 2), o = {
					type: "symb",
					mode: e.mode,
					text: "\\sqrt",
					bbox: {
						x: n + a,
						y: r + t / 2,
						w: e.chld[0].bbox.x - a,
						h: e.bbox.h - t / 2
					},
					chld: []
				};
				i.push(o), i.push({
					type: "symb",
					text: "\\bar",
					mode: e.mode,
					bbox: {
						x: n + e.chld[0].bbox.x,
						y: r,
						w: e.bbox.w - e.chld[0].bbox.x,
						h: t
					},
					chld: []
				});
			} else if (e.text == "\\binom") {
				let t = Math.min(e.chld[0].bbox.x, e.chld[1].bbox.x), a = {
					type: "symb",
					mode: e.mode,
					text: "(",
					bbox: {
						x: n,
						y: r,
						w: t,
						h: e.bbox.h
					},
					chld: []
				};
				i.push(a), i.push({
					type: "symb",
					text: ")",
					mode: e.mode,
					bbox: {
						x: n + e.bbox.w - t,
						y: r,
						w: t,
						h: e.bbox.h
					},
					chld: []
				});
			} else if (U[e.text] && U[e.text].flags.hat) {
				let t = e.chld[0].bbox.y, a = {
					type: "symb",
					mode: e.mode,
					text: e.text,
					bbox: {
						x: n,
						y: r,
						w: e.bbox.w,
						h: t
					},
					chld: []
				};
				i.push(a);
			} else if (U[e.text] && U[e.text].flags.mat) {
				let t = e.chld[0].bbox.h, a = {
					type: "symb",
					text: e.text,
					mode: e.mode,
					bbox: {
						x: n,
						y: r + t,
						w: e.bbox.w,
						h: e.bbox.h - t
					},
					chld: []
				};
				i.push(a);
			} else if (e.type != "node" && e.text != "^" && e.text != "_") {
				let t = {
					type: e.type == "func" ? "symb" : e.type,
					text: e.text,
					mode: e.mode,
					bbox: {
						x: n,
						y: r,
						w: e.bbox.w,
						h: e.bbox.h
					},
					chld: []
				};
				i.push(t);
			}
		}
		for (let a = 0; a < e.chld.length; a++) {
			let o = t(e.chld[a], n, r);
			i.push(...o);
		}
		return i;
	}
	let n = t(e, -e.bbox.x, -e.bbox.y);
	e.type = "node", e.text = "", e.chld = n;
}
function ut(e) {
	let t = [];
	for (let n = 0; n < e.chld.length; n++) {
		let r = e.chld[n], i = r.bbox.h / 2, a = !1;
		if (U[r.text] && U[r.text].flags.hat && !U[r.text].flags.xfl && !U[r.text].flags.yfl && (i *= 4, a = !0), U[r.text] && U[r.text].glyph) {
			let e = Je(U[r.text].glyph);
			for (let n = 0; n < e.polylines.length; n++) {
				let o = [];
				for (let t = 0; t < e.polylines[n].length; t++) {
					let s = e.polylines[n][t][0], c = e.polylines[n][t][1];
					if (U[r.text].flags.xfl) s = (s - e.xmin) / Math.max(e.xmax - e.xmin, 1) * r.bbox.w, s += r.bbox.x;
					else if (e.w / 16 * i > r.bbox.w) s = s / Math.max(e.w, 1) * r.bbox.w, s += r.bbox.x;
					else {
						s = s / 16 * i;
						let t = (r.bbox.w - e.w / 16 * i) / 2;
						s += r.bbox.x + t;
					}
					if (U[r.text].flags.yfl) c = (c - e.ymin) / Math.max(e.ymax - e.ymin, 1) * r.bbox.h, c += r.bbox.y;
					else {
						if (c = c / 16 * i, a) {
							let t = (e.ymax + e.ymin) / 2;
							c -= t / 16 * i;
						}
						c += r.bbox.y + r.bbox.h / 2;
					}
					o.push([s, c]);
				}
				t.push(o);
			}
		} else if (U[r.text] && U[r.text].flags.txt || r.type == "char") {
			let e = r.bbox.x, n = !!(U[r.text] && U[r.text].flags.txt);
			for (let a = Number(n); a < r.text.length; a++) {
				let o = Je(Qe(r.text[a], n ? "text" : r.mode));
				if (!o) {
					console.warn("unmapped character: " + r.text[a]);
					continue;
				}
				for (let n = 0; n < o.polylines.length; n++) {
					let a = [];
					for (let t = 0; t < o.polylines[n].length; t++) {
						let s = o.polylines[n][t][0], c = o.polylines[n][t][1];
						s /= 16, c /= 16, s *= i, c *= i, r.mode == "tt" && (o.w > 16 ? s *= 16 / o.w : s += (16 - o.w) / 2 / 16), s += e, c += r.bbox.y + r.bbox.h / 2, a.push([s, c]);
					}
					t.push(a);
				}
				r.mode == "tt" ? e += i : e += o.w / 16 * i;
			}
		}
	}
	return t;
}
function dt(e) {
	return Math.round(e * 100) / 100;
}
var ft = class {
	_latex;
	_tree;
	_tokens;
	_polylines;
	constructor(e) {
		this._latex = e, this._tokens = et(e), this._tree = nt(this._tokens), rt(this._tree.chld), ct(this._tree), lt(this._tree), this._polylines = ut(this._tree);
	}
	resolveScale(e) {
		if (e == null) return [
			16,
			16,
			16,
			16
		];
		let t = e.SCALE_X ?? 16, n = e.SCALE_Y ?? 16;
		if (e.MIN_CHAR_H != null) {
			let r = 0;
			for (let e = 0; e < this._tree.chld.length; e++) {
				let t = this._tree.chld[e];
				(t.type == "char" || U[t.text] && (U[t.text].flags.txt || !Object.keys(U[t.text].flags).length)) && (r = Math.min(t.bbox.h, r));
			}
			let i = Math.max(1, e.MIN_CHAR_H / r);
			t *= i, n *= i;
		}
		if (e.MAX_W != null) {
			let r = t;
			t = Math.min(t, e.MAX_W / this._tree.bbox.w), n *= t / r;
		}
		if (e.MAX_H != null) {
			let r = n;
			n = Math.min(n, e.MAX_H / this._tree.bbox.h), t *= n / r;
		}
		return [
			e.MARGIN_X ?? t,
			e.MARGIN_Y ?? n,
			t,
			n
		];
	}
	polylines(e) {
		e ||= {};
		let t = [], [n, r, i, a] = this.resolveScale(e);
		for (let e = 0; e < this._polylines.length; e++) {
			t.push([]);
			for (let o = 0; o < this._polylines[e].length; o++) {
				let [s, c] = this._polylines[e][o];
				t[t.length - 1].push([n + s * i, r + c * a]);
			}
		}
		return t;
	}
	pathd(e) {
		e ||= {};
		let t = "", [n, r, i, a] = this.resolveScale(e);
		for (let e = 0; e < this._polylines.length; e++) for (let o = 0; o < this._polylines[e].length; o++) {
			let [s, c] = this._polylines[e][o];
			t += o ? "L" : "M", t += `${dt(n + s * i)} ${dt(r + c * a)}`;
		}
		return t;
	}
	svg(e) {
		e ||= {};
		let [t, n, r, i] = this.resolveScale(e), a = dt(this._tree.bbox.w * r + t * 2), o = dt(this._tree.bbox.h * i + n * 2), s = `<svg
      xmlns="http://www.w3.org/2000/svg"
      width="${a}" height="${o}"
      fill="none" stroke="${e.FG_COLOR ?? "black"}" stroke-width="${e.STROKE_W ?? 1}"
      stroke-linecap="round" stroke-linejoin="round"
    >`;
		e.BG_COLOR && (s += `<rect x="0" y="0" width="${a}" height="${o}" fill="${e.BG_COLOR}" stroke="none"></rect>`), s += "<path d=\"";
		for (let e = 0; e < this._polylines.length; e++) {
			s += "M";
			for (let a = 0; a < this._polylines[e].length; a++) {
				let [o, c] = this._polylines[e][a];
				s += dt(t + o * r) + " " + dt(n + c * i) + " ";
			}
		}
		return s += "\"/>", s += "</svg>", {
			svg: `data:image/svg+xml;base64,${window.btoa(s)}`,
			width: Math.ceil(a),
			height: Math.ceil(o)
		};
	}
	pdf(e) {
		e ||= {};
		let [t, n, r, i] = this.resolveScale(e), a = dt(this._tree.bbox.w * r + t * 2), o = dt(this._tree.bbox.h * i + n * 2), s = `%PDF-1.1\n%%¥±ë\n1 0 obj\n<< /Type /Catalog\n/Pages 2 0 R\n>>endobj
    2 0 obj\n<< /Type /Pages\n/Kids [3 0 R]\n/Count 1\n/MediaBox [0 0 ${a} ${o}]\n>>\nendobj
    3 0 obj\n<< /Type /Page\n/Parent 2 0 R\n/Resources\n<< /Font\n<< /F1\n<< /Type /Font
    /Subtype /Type1\n/BaseFont /Times-Roman\n>>\n>>\n>>\n/Contents [`, c = "", l = 4;
		for (let a = 0; a < this._polylines.length; a++) {
			c += `${l} 0 obj \n<< /Length 0 >>\n stream\n 1 j 1 J ${e.STROKE_W ?? 1} w\n`;
			for (let e = 0; e < this._polylines[a].length; e++) {
				let [s, l] = this._polylines[a][e];
				c += `${dt(t + s * r)} ${dt(o - (n + l * i))} ${e ? "l" : "m"} `;
			}
			c += "\nS\nendstream\nendobj\n", s += `${l} 0 R `, l++;
		}
		return s += "]\n>>\nendobj\n", c += "\ntrailer\n<< /Root 1 0 R \n /Size 0\n >>startxref\n\n%%EOF\n", s + c;
	}
	boxes(e) {
		e ||= {};
		let [t, n, r, i] = this.resolveScale(e), a = [];
		for (let e = 0; e < this._tree.chld.length; e++) {
			let { x: o, y: s, w: c, h: l } = this._tree.chld[e].bbox;
			a.push({
				x: t + o * r,
				y: n + s * i,
				w: c * r,
				h: l * i
			});
		}
		return a;
	}
	box(e) {
		e ||= {};
		let [t, n, r, i] = this.resolveScale(e);
		return {
			x: t + this._tree.bbox.x * r,
			y: n + this._tree.bbox.y * i,
			w: this._tree.bbox.w * r,
			h: this._tree.bbox.h * i
		};
	}
}, pt = class extends Ke {
	static convertLaTextToSVG(e) {
		return new ft(e).svg({
			SCALE_X: 10,
			SCALE_Y: 10,
			MARGIN_X: 0,
			MARGIN_Y: 0
		});
	}
	render(e, t, n, r) {
		let { scale: i } = this.options, a = t.width * i, o = t.height * i;
		if (this.imageCache.has(t.value)) {
			let i = this.imageCache.get(t.value);
			e.drawImage(i, n, r, a, o);
		} else {
			let i = new Promise((i, s) => {
				let c = new Image();
				c.src = t.laTexSVG, c.onload = () => {
					e.drawImage(c, n, r, a, o), this.imageCache.set(t.value, c), i(t);
				}, c.onerror = (e) => {
					s(e);
				};
			});
			this.addImageObserver(i);
		}
	}
}, mt;
(function(e) {
	e.UL = "ul", e.OL = "ol";
})(mt ||= {});
var ht;
(function(e) {
	e.DISC = "disc", e.CIRCLE = "circle", e.SQUARE = "square", e.CHECKBOX = "checkbox";
})(ht ||= {});
var gt;
(function(e) {
	e.DECIMAL = "decimal";
})(gt ||= {});
var _t;
(function(e) {
	e.DISC = "disc", e.CIRCLE = "circle", e.SQUARE = "square", e.DECIMAL = "decimal", e.CHECKBOX = "checkbox";
})(_t ||= {});
//#endregion
//#region src/editor/dataset/constant/List.ts
var vt = { inheritStyle: !1 }, yt = {
	[ht.DISC]: "•",
	[ht.CIRCLE]: "◦",
	[ht.SQUARE]: "▫︎",
	[ht.CHECKBOX]: "☑️"
}, bt = {
	[mt.OL]: "ol",
	[mt.UL]: "ul"
}, xt = {
	[_t.DISC]: "disc",
	[_t.CIRCLE]: "circle",
	[_t.SQUARE]: "square",
	[_t.DECIMAL]: "decimal",
	[_t.CHECKBOX]: "checkbox"
}, W;
(function(e) {
	e.FIRST = "first", e.SECOND = "second", e.THIRD = "third", e.FOURTH = "fourth", e.FIFTH = "fifth", e.SIXTH = "sixth";
})(W ||= {});
//#endregion
//#region src/editor/dataset/constant/Title.ts
var St = {
	defaultFirstSize: 26,
	defaultSecondSize: 24,
	defaultThirdSize: 22,
	defaultFourthSize: 20,
	defaultFifthSize: 18,
	defaultSixthSize: 16
}, Ct = {
	[W.FIRST]: "defaultFirstSize",
	[W.SECOND]: "defaultSecondSize",
	[W.THIRD]: "defaultThirdSize",
	[W.FOURTH]: "defaultFourthSize",
	[W.FIFTH]: "defaultFifthSize",
	[W.SIXTH]: "defaultSixthSize"
}, wt = {
	[W.FIRST]: 1,
	[W.SECOND]: 2,
	[W.THIRD]: 3,
	[W.FOURTH]: 4,
	[W.FIFTH]: 5,
	[W.SIXTH]: 6
}, Tt = {
	H1: W.FIRST,
	H2: W.SECOND,
	H3: W.THIRD,
	H4: W.FOURTH,
	H5: W.FIFTH,
	H6: W.SIXTH
}, Et;
(function(e) {
	e.IFRAME = "iframe", e.VIDEO = "video";
})(Et ||= {});
//#endregion
//#region src/editor/dataset/enum/Control.ts
var G;
(function(e) {
	e.TEXT = "text", e.SELECT = "select", e.CHECKBOX = "checkbox", e.RADIO = "radio", e.DATE = "date", e.NUMBER = "number";
})(G ||= {});
var K;
(function(e) {
	e.PREFIX = "prefix", e.POSTFIX = "postfix", e.PRE_TEXT = "preText", e.POST_TEXT = "postText", e.PLACEHOLDER = "placeholder", e.VALUE = "value", e.CHECKBOX = "checkbox", e.RADIO = "radio";
})(K ||= {});
var Dt;
(function(e) {
	e.ROW_START = "rowStart", e.VALUE_START = "valueStart";
})(Dt ||= {});
var Ot;
(function(e) {
	e.ACTIVE = "active", e.INACTIVE = "inactive";
})(Ot ||= {});
var q;
(function(e) {
	e.NUMBER = "number", e.OPERATOR = "operator", e.UTILITY = "utility", e.EQUAL = "equal";
})(q ||= {});
//#endregion
//#region src/editor/dataset/enum/Trace.ts
var J;
(function(e) {
	e.INSERTED = "inserted", e.DELETED = "deleted";
})(J ||= {});
//#endregion
//#region src/editor/dataset/enum/table/Table.ts
var kt;
(function(e) {
	e.ALL = "all", e.EMPTY = "empty", e.EXTERNAL = "external", e.INTERNAL = "internal", e.DASH = "dash";
})(kt ||= {});
var At;
(function(e) {
	e.TOP = "top", e.RIGHT = "right", e.BOTTOM = "bottom", e.LEFT = "left";
})(At ||= {});
var jt;
(function(e) {
	e.FORWARD = "forward", e.BACK = "back";
})(jt ||= {});
//#endregion
//#region src/editor/dataset/enum/Background.ts
var Mt;
(function(e) {
	e.CONTAIN = "contain", e.COVER = "cover";
})(Mt ||= {});
var Nt;
(function(e) {
	e.REPEAT = "repeat", e.NO_REPEAT = "no-repeat", e.REPEAT_X = "repeat-x", e.REPEAT_Y = "repeat-y";
})(Nt ||= {});
//#endregion
//#region src/editor/dataset/constant/Background.ts
var Pt = {
	color: "#FFFFFF",
	image: "",
	size: Mt.COVER,
	repeat: Nt.NO_REPEAT,
	applyPageNumbers: []
}, Y;
(function(e) {
	e.TOP = "top", e.MIDDLE = "middle", e.BOTTOM = "bottom";
})(Y ||= {});
//#endregion
//#region src/editor/dataset/constant/Checkbox.ts
var Ft = {
	width: 14,
	height: 14,
	gap: 5,
	lineWidth: 1,
	fillStyle: "#ffffff",
	strokeStyle: "#000000",
	checkFillStyle: "#5175f4",
	checkStrokeStyle: "#5175f4",
	checkMarkColor: "#ffffff",
	verticalAlign: Y.BOTTOM
}, It = {
	placeholderColor: "#9c9b9b",
	bracketColor: "#000000",
	prefix: "{",
	postfix: "}",
	borderWidth: 1,
	borderColor: "#000000",
	activeBackgroundColor: "",
	disabledBackgroundColor: "",
	existValueBackgroundColor: "",
	noValueBackgroundColor: "",
	errorBackgroundColor: "#FFECE8"
}, Lt = {
	bottom: 30,
	inactiveAlpha: 1,
	maxHeightRadio: t.HALF,
	disabled: !1,
	editable: !0,
	disabledPages: []
}, Rt = {
	opacity: .1,
	backgroundColor: "#E99D00",
	activeOpacity: .5,
	activeBackgroundColor: "#E99D00",
	disabled: !1,
	deletable: !0
}, zt = {
	top: 30,
	inactiveAlpha: 1,
	maxHeightRadio: t.HALF,
	disabled: !1,
	editable: !0,
	disabledPages: []
}, Bt = {
	defaultColor: "#1976d2",
	defaultBackgroundColor: "#e3f2fd",
	defaultBorderRadius: 4,
	defaultPadding: [
		4,
		4,
		4,
		4
	]
}, Vt = {
	color: "#666666",
	font: "Microsoft YaHei",
	size: 12,
	top: 5
}, Ht = {
	disabled: !0,
	color: "#CCCCCC",
	lineWidth: 1.5
}, Ut = {
	font: "Microsoft YaHei",
	fontSize: 12,
	lineDash: [3, 1]
}, Wt = {
	PAGE_NO: "{pageNo}",
	PAGE_COUNT: "{pageCount}"
}, Gt = {
	bottom: 60,
	size: 12,
	font: "Microsoft YaHei",
	color: "#000000",
	rowFlex: u.CENTER,
	format: Wt.PAGE_NO,
	numberType: n.ARABIC,
	disabled: !1,
	startPageNo: 1,
	fromPageNo: 0,
	maxPageNo: null
}, Kt = {
	data: "",
	color: "#DCDFE6",
	opacity: 1,
	size: 16,
	font: "Microsoft YaHei"
}, qt = {
	width: 14,
	height: 14,
	gap: 5,
	lineWidth: 1,
	fillStyle: "#5175f4",
	strokeStyle: "#000000",
	verticalAlign: Y.BOTTOM
}, Jt = {
	lineWidth: 1,
	strokeStyle: "#000000"
}, Yt = {
	tdPadding: [
		0,
		5,
		5,
		5
	],
	defaultTrMinHeight: 42,
	defaultColMinWidth: 40,
	defaultBorderColor: "#000000",
	overflow: !1
}, Xt;
(function(e) {
	e.TEXT = "text", e.IMAGE = "image";
})(Xt ||= {});
var Zt;
(function(e) {
	e.BOTTOM = "bottom", e.TOP = "top";
})(Zt ||= {});
//#endregion
//#region src/editor/dataset/constant/Watermark.ts
var Qt = {
	data: "",
	type: Xt.TEXT,
	width: 0,
	height: 0,
	color: "#AEB5C0",
	opacity: .3,
	size: 200,
	font: "Microsoft YaHei",
	repeat: !1,
	gap: [10, 10],
	numberType: n.ARABIC,
	layer: Zt.BOTTOM
}, $t = { tipDisabled: !0 }, en;
(function(e) {
	e.PAGE = "page", e.CONTINUITY = "continuity";
})(en ||= {});
//#endregion
//#region src/editor/dataset/constant/LineNumber.ts
var tn = {
	size: 12,
	font: "Microsoft YaHei",
	color: "#000000",
	disabled: !0,
	right: 20,
	type: en.CONTINUITY
}, nn = {
	disabled: !0,
	size: 120,
	zoom: 2,
	borderColor: "#efefef"
}, rn = { disabled: !0 }, an = {
	count: 1,
	gap: 20,
	separator: !1,
	separatorColor: "#000000",
	separatorWidth: 1
}, on = {
	disabled: !0,
	backgroundColor: "#fff",
	color: "#000000",
	fontSize: 12,
	maxWidth: 280
}, sn = {
	color: "#000000",
	lineWidth: 1,
	padding: [
		0,
		5,
		0,
		5
	],
	disabled: !0
}, cn = {
	top: 0,
	left: 5
}, ln = {
	defaultLineColor: "#000000",
	defaultLineWidth: 2
}, un = {
	disabled: !0,
	color: "#CCCCCC",
	radius: 1
}, dn = {
	disabled: !0,
	insertColor: "#2B5CE6",
	deleteColor: "#E03F3F",
	author: "",
	lineWidth: 2
}, fn = {
	disabled: !0,
	height: 26
}, pn = {
	disabled: !0,
	color: "#FF0000"
};
//#endregion
//#region src/editor/utils/option.ts
function mn(e = {}) {
	let t = {
		...Yt,
		...e.table
	}, n = {
		...zt,
		...e.header
	}, r = {
		...Lt,
		...e.footer
	}, i = {
		...Gt,
		...e.pageNumber
	}, a = {
		...Qt,
		...e.watermark
	}, o = {
		...It,
		...e.control
	}, s = {
		...Ft,
		...e.checkbox
	}, c = {
		...qt,
		...e.radio
	}, u = {
		...ge,
		...e.cursor
	}, d = {
		...St,
		...e.title
	}, f = {
		...Kt,
		...e.placeholder
	}, m = {
		...Rt,
		...e.group
	}, y = {
		...Ut,
		...e.pageBreak
	}, b = {
		...$t,
		...e.zone
	}, x = {
		...Pt,
		...e.background
	}, S = {
		...Ht,
		...e.lineBreak
	}, C = {
		...un,
		...e.whiteSpace
	}, w = {
		...Jt,
		...e.separator
	}, T = {
		...tn,
		...e.lineNumber
	}, E = {
		...sn,
		...e.pageBorder
	}, D = {
		...cn,
		...e.badge
	}, O = {
		...ln,
		...e.graffiti
	}, k = {
		...Bt,
		...e.label
	}, A = {
		...Vt,
		...e.imgCaption
	}, j = {
		...vt,
		...e.list
	}, M = {
		...nn,
		...e.magnifier
	}, N = {
		...rn,
		...e.accessibility
	}, ee = {
		...an,
		...e.column
	}, P = {
		...dn,
		...e.trace
	}, F = {
		...fn,
		...e.ruler
	}, I = {
		...on,
		...e.hint
	}, te = {
		...pn,
		...e.spellcheck
	}, L = {
		print: {
			...ye.print,
			...e.modeRule?.print
		},
		readonly: {
			...ye.readonly,
			...e.modeRule?.readonly
		},
		form: {
			...ye.form,
			...e.modeRule?.form
		}
	};
	return {
		mode: p.EDIT,
		locale: "zhCN",
		defaultType: "TEXT",
		defaultColor: "#000000",
		defaultFont: "Microsoft YaHei",
		defaultSize: 16,
		minSize: 5,
		maxSize: 72,
		defaultRowMargin: 1,
		defaultBasicRowMarginHeight: 8,
		defaultTabWidth: 32,
		width: 794,
		height: 1123,
		scale: 1,
		pageGap: 20,
		underlineColor: "#000000",
		strikeoutColor: "#FF0000",
		rangeAlpha: .6,
		rangeColor: "#AECBFA",
		rangeMinWidth: 5,
		searchMatchAlpha: .6,
		searchMatchColor: "#FFFF00",
		searchNavigateMatchColor: "#AAD280",
		highlightAlpha: .6,
		highlightMarginHeight: 8,
		resizerColor: "#4182D9",
		resizerSize: 5,
		marginIndicatorSize: 35,
		marginIndicatorColor: "#BABABA",
		margins: [
			100,
			120,
			100,
			120
		],
		pageMode: h.PAGING,
		renderMode: v.SPEED,
		defaultHyperlinkColor: "#0000FF",
		paperDirection: g.VERTICAL,
		inactiveAlpha: .6,
		historyMaxRecordCount: 100,
		wordBreak: _.BREAK_WORD,
		printPixelRatio: 3,
		maskMargin: [
			0,
			0,
			0,
			0
		],
		letterClass: [l.ENGLISH],
		contextMenuDisableKeys: [],
		shortcutDisableKeys: [],
		scrollContainerSelector: "",
		pageOuterSelectionDisable: !1,
		...e,
		table: t,
		header: n,
		footer: r,
		pageNumber: i,
		watermark: a,
		control: o,
		checkbox: s,
		radio: c,
		cursor: u,
		title: d,
		placeholder: f,
		group: m,
		pageBreak: y,
		zone: b,
		background: x,
		lineBreak: S,
		whiteSpace: C,
		separator: w,
		lineNumber: T,
		pageBorder: E,
		badge: D,
		modeRule: L,
		graffiti: O,
		label: k,
		imgCaption: A,
		list: j,
		magnifier: M,
		accessibility: N,
		column: ee,
		trace: P,
		ruler: F,
		hint: I,
		spellcheck: te
	};
}
//#endregion
//#region src/editor/utils/element.ts
function hn(e) {
	let t = e.trace;
	return t?.[t.length - 1]?.type === J.DELETED;
}
function gn(e) {
	let t = k(e), n = (e) => e.filter((e) => {
		if (hn(e)) return !1;
		e.valueList &&= n(e.valueList), e.control?.value && (e.control.value = n(e.control.value));
		for (let t of e.trList || []) for (let e of t.tdList) e.value = n(e.value);
		return !0;
	});
	return n(t);
}
function _n(e) {
	let t = gn(e), n = (e) => {
		for (let t of e) {
			delete t.trace, t.valueList && n(t.valueList), t.control?.value && n(t.control.value);
			for (let e of t.trList || []) for (let t of e.tdList) n(t.value);
		}
	};
	return n(t), t;
}
function vn(e) {
	let t = [];
	for (let n = 0; n < e.length; n++) {
		let r = e[n], i = N(r.value);
		for (let e = 0; e < i.length; e++) t.push({
			...r,
			value: i[e]
		});
	}
	return t;
}
function yn(e, t) {
	let { isHandleFirstElement: n = !0, isForceCompensation: r = !1, editorOptions: i } = t, a = e[0];
	a?.type !== H.LIST && (r || n && (a?.type && a.type !== H.TEXT || !C.test(a?.value))) && e.unshift({ value: "​" });
	let o = 0;
	for (; o < e.length;) {
		let n = e[o];
		if (n.type === H.TITLE) {
			e.splice(o, 1);
			let r = n.valueList || [];
			if (yn(r, {
				...t,
				isHandleFirstElement: !1,
				isForceCompensation: !1
			}), r.length) {
				let t = n.titleId || M(), a = i.title;
				for (let i = 0; i < r.length; i++) {
					let s = r[i];
					s.title = n.title, n.hint && !s.hint && (s.hint = n.hint), n.level && (s.titleId = t, s.level = n.level), Tn(s) && (s.size ||= a[Ct[s.level]], s.bold === void 0 && (s.bold = !0)), e.splice(o, 0, s), o++;
				}
			}
			o--;
		} else if (n.type === H.LIST) {
			e.splice(o, 1);
			let r = n.valueList || [];
			if (yn(r, {
				...t,
				isHandleFirstElement: !0,
				isForceCompensation: !1
			}), r.length) {
				let t = n.listId || M(), i = /* @__PURE__ */ new Map([[0, t]]);
				for (let t = 0; t < r.length; t++) {
					let a = r[t], s = a.listLevel ?? n.listLevel ?? 0;
					a.listId ||= i.get(s) || M(), i.set(s, a.listId), Array.from(i.keys()).forEach((e) => {
						e > s && i.delete(e);
					}), a.listType = a.listType || n.listType, a.listStyle = a.listStyle || n.listStyle, a.listLevel = s, n.hint && !a.hint && (a.hint = n.hint), e.splice(o, 0, a), o++;
				}
				e[o] && (e[o].valueList?.length ? !C.test(e[o].valueList[0].value) : !C.test(e[o].value)) && (e.splice(o, 0, { value: "​" }), o++);
			}
			o--;
		} else if (n.type === H.AREA) {
			e.splice(o, 1);
			let r = n?.valueList || [];
			if (yn(r, {
				...t,
				isHandleFirstElement: !0,
				isForceCompensation: !0
			}), r.length) {
				let t = M();
				for (let i = 0; i < r.length; i++) {
					let a = r[i];
					if (a.areaId = n.areaId || t, a.area = n.area, a.areaIndex = i, n.hint && !a.hint && (a.hint = n.hint), a.type === H.TABLE) {
						let e = a.trList;
						for (let r = 0; r < e.length; r++) {
							let i = e[r];
							for (let e = 0; e < i.tdList.length; e++) {
								let r = i.tdList[e].value;
								for (let e = 0; e < r.length; e++) {
									let i = r[e];
									i.areaId = n.areaId || t, i.area = n.area;
								}
							}
						}
					}
					e.splice(o, 0, a), o++;
				}
			}
			o--;
		} else if (n.type === H.TABLE) {
			let e = n.id || M();
			if (n.id = e, n.trList) {
				let { table: { defaultTrMinHeight: r, defaultColMinWidth: a }, margins: o } = i;
				if (!n.colgroup?.length && n.trList.length) {
					let e = n.trList[0].tdList.reduce((e, t) => e + t.colspan, 0), t = i.width - o[1] - o[3], r = Math.max(t / e, a);
					n.colgroup = [];
					for (let t = 0; t < e; t++) n.colgroup.push({ width: r });
				}
				for (let i = 0; i < n.trList.length; i++) {
					let a = n.trList[i], o = a.id || M();
					a.id = o, (!a.minHeight || a.minHeight < r) && (a.minHeight = r), a.height < a.minHeight && (a.height = a.minHeight);
					for (let n = 0; n < a.tdList.length; n++) {
						let r = a.tdList[n], i = r.id || M();
						r.id = i, yn(r.value, {
							...t,
							isHandleFirstElement: !0,
							isForceCompensation: !0
						}), !r.value[0].size && r.value[1]?.size && Tn(r.value[1]) && (r.value[0].size = r.value[1].size);
						for (let t = 0; t < r.value.length; t++) {
							let n = r.value[t];
							n.tdId = i, n.trId = o, n.tableId = e;
						}
					}
				}
			}
		} else if (n.type === H.HYPERLINK) {
			e.splice(o, 1);
			let t = vn(n.valueList || []);
			if (t.length) {
				let r = M();
				for (let i = 0; i < t.length; i++) {
					let a = t[i];
					a.type = n.type, a.url = n.url, a.hyperlinkId = r, n.hint && !a.hint && (a.hint = n.hint), e.splice(o, 0, a), o++;
				}
			}
			o--;
		} else if (n.type === H.DATE) {
			e.splice(o, 1);
			let t = vn(n.valueList || []);
			if (t.length) {
				let r = M();
				for (let i = 0; i < t.length; i++) {
					let a = t[i];
					a.type = n.type, a.dateFormat = n.dateFormat, a.dateId = r, e.splice(o, 0, a), o++;
				}
			}
			o--;
		} else if (n.type === H.CONTROL) {
			if (!n.control) {
				o++;
				continue;
			}
			let { prefix: r, postfix: a, preText: s, postText: c, value: l, placeholder: u, code: d, type: f, valueSets: p } = n.control, { editorOptions: { control: m, checkbox: h, radio: g } } = t, _ = n.controlId || M();
			e.splice(o, 1);
			let v = V(n, [
				...ze,
				...Ee,
				...De,
				...Oe
			]), y = V(n.control, Le), b = {
				...y,
				color: i.control.bracketColor
			}, x = N(r || m.prefix);
			for (let t = 0; t < x.length; t++) {
				let r = x[t];
				e.splice(o, 0, {
					...v,
					...b,
					controlId: _,
					value: r,
					type: n.type,
					control: n.control,
					controlComponent: K.PREFIX
				}), o++;
			}
			if (s) {
				let t = N(s);
				for (let r = 0; r < t.length; r++) {
					let i = t[r];
					e.splice(o, 0, {
						...v,
						...y,
						controlId: _,
						value: i,
						type: n.type,
						control: n.control,
						controlComponent: K.PRE_TEXT
					}), o++;
				}
			}
			if (l && l.length || f === G.CHECKBOX || f === G.RADIO || f === G.SELECT && d && (!l || !l.length)) {
				let r = l ? k(l) : [];
				if (f === G.CHECKBOX) {
					let t = d ? d.split(",") : [];
					if (Array.isArray(p) && p.length) {
						let i = r.reduce((e, t) => e.concat(t.value.split("").map((e) => ({
							...t,
							value: e
						}))), []), a = 0;
						for (let r = 0; r < p.length; r++) {
							let s = p[r];
							e.splice(o, 0, {
								...v,
								...y,
								controlId: _,
								value: "",
								type: n.type,
								control: n.control,
								controlComponent: K.CHECKBOX,
								checkbox: {
									code: s.code,
									value: t.includes(s.code)
								}
							}), o++;
							let c = N(s.value);
							for (let t = 0; t < c.length; t++) {
								let r = c[t], s = t === c.length - 1;
								e.splice(o, 0, {
									...v,
									...y,
									...i[a],
									controlId: _,
									value: r === "\n" ? "​" : r,
									letterSpacing: s ? h.gap : 0,
									control: n.control,
									controlComponent: K.VALUE
								}), a++, o++;
							}
						}
					}
				} else if (f === G.RADIO) {
					if (Array.isArray(p) && p.length) {
						let t = r.reduce((e, t) => e.concat(t.value.split("").map((e) => ({
							...t,
							value: e
						}))), []), i = 0;
						for (let r = 0; r < p.length; r++) {
							let a = p[r];
							e.splice(o, 0, {
								...v,
								...y,
								controlId: _,
								value: "",
								type: n.type,
								control: n.control,
								controlComponent: K.RADIO,
								radio: {
									code: a.code,
									value: d === a.code
								}
							}), o++;
							let s = N(a.value);
							for (let r = 0; r < s.length; r++) {
								let a = s[r], c = r === s.length - 1;
								e.splice(o, 0, {
									...v,
									...y,
									...t[i],
									controlId: _,
									value: a === "\n" ? "​" : a,
									letterSpacing: c ? g.gap : 0,
									control: n.control,
									controlComponent: K.VALUE
								}), i++, o++;
							}
						}
					}
				} else {
					if ((!l || !l.length) && Array.isArray(p) && p.length) {
						let e = p.find((e) => e.code === d);
						e && (r = [{ value: e.value }]);
					}
					yn(r, {
						...t,
						isHandleFirstElement: !1,
						isForceCompensation: !1
					});
					for (let t = 0; t < r.length; t++) {
						let i = r[t], a = i.value, s = !!i.controlId && i.controlId !== _;
						e.splice(o, 0, {
							...v,
							...y,
							...i,
							...s ? {} : {
								controlId: _,
								control: n.control,
								controlComponent: K.VALUE
							},
							value: a === "\n" ? "​" : a,
							type: i.type || H.TEXT
						}), o++;
					}
				}
			} else if (u) {
				let t = {
					...y,
					color: i.control.placeholderColor
				}, r = N(u);
				for (let i = 0; i < r.length; i++) {
					let a = r[i];
					e.splice(o, 0, {
						...v,
						...t,
						controlId: _,
						value: a === "\n" ? "​" : a,
						type: n.type,
						control: n.control,
						controlComponent: K.PLACEHOLDER
					}), o++;
				}
			}
			if (c) {
				let t = N(c);
				for (let r = 0; r < t.length; r++) {
					let i = t[r];
					e.splice(o, 0, {
						...v,
						...y,
						controlId: _,
						value: i,
						type: n.type,
						control: n.control,
						controlComponent: K.POST_TEXT
					}), o++;
				}
			}
			let S = N(a || m.postfix);
			for (let t = 0; t < S.length; t++) {
				let r = S[t];
				e.splice(o, 0, {
					...v,
					...b,
					controlId: _,
					value: r,
					type: n.type,
					control: n.control,
					controlComponent: K.POSTFIX
				}), o++;
			}
			o--;
		} else if ((!n.type || Be.includes(n.type)) && n.value?.length > 1) {
			e.splice(o, 1);
			let t = N(n.value);
			for (let r = 0; r < t.length; r++) e.splice(o + r, 0, {
				...n,
				value: t[r]
			});
			n = e[o];
		}
		if ((n.value === "\n" || n.value == "\r\n") && (n.value = "​"), (n.type === H.IMAGE || n.type === H.BLOCK) && (n.id = n.id || M()), n.type === H.LATEX) {
			let { svg: e, width: t, height: r } = pt.convertLaTextToSVG(n.value);
			n.width = n.width || t, n.height = n.height || r, n.laTexSVG = e, n.id = n.id || M();
		}
		o++;
	}
}
function bn(e, t) {
	let n = Object.keys(e), r = Object.keys(t);
	if (n.length !== r.length) return !1;
	for (let r = 0; r < n.length; r++) {
		let i = n[r];
		if (i !== "value" && !(i === "groupIds" && Array.isArray(e[i]) && Array.isArray(t[i]) && ce(e[i], t[i]))) {
			if (i === "trace") {
				let n = e[i] || [], r = t[i] || [];
				if (n.length !== r.length) return !1;
				for (let e = 0; e < n.length; e++) {
					let t = n[e], i = r[e];
					if (t.type !== i.type || t.author !== i.author || t.timestamp !== i.timestamp) return !1;
				}
				continue;
			}
			if (e[i] !== t[i]) return !1;
		}
	}
	return !0;
}
function xn(e, t = {}) {
	let { extraPickAttrs: n } = t, r = [...je];
	n && r.push(...n);
	let i = { value: e.value === "​" ? "\n" : e.value };
	return r.forEach((t) => {
		let n = e[t];
		n !== void 0 && (i[t] = n);
	}), i;
}
function X(e, t = {}) {
	let { extraPickAttrs: n, isClassifyArea: r = !1, isClone: i = !0, isListValue: a = !1 } = t, o = i ? k(e) : e, s = [], c = 0;
	for (; c < o.length;) {
		let e = o[c];
		if (c === 0 && e.value === "​" && !e.listId && (!e.type || e.type === H.TEXT)) {
			c++;
			continue;
		}
		if (e.areaId) {
			let n = e.areaId, i = e.area, a = [];
			for (; c < o.length;) {
				let e = o[c];
				if (n !== e.areaId) {
					c--;
					break;
				}
				delete e.area, delete e.areaId, a.push(e), c++;
			}
			let l = X(a, t);
			if (r) {
				let t = {
					type: H.AREA,
					value: "",
					areaId: n,
					area: i
				};
				t.valueList = l, e = t;
			} else {
				s.splice(c, 0, ...l);
				continue;
			}
		} else if (e.titleId && e.level) {
			let n = e.titleId;
			if (n) {
				let r = e.level, i = {
					type: H.TITLE,
					title: e.title,
					titleId: n,
					value: "",
					level: r
				}, a = [];
				for (; c < o.length;) {
					let e = o[c];
					if (n !== e.titleId) {
						c--;
						break;
					}
					delete e.level, delete e.title, a.push(e), c++;
				}
				i.valueList = X(a, t), e = i;
			}
		} else if (!a && e.listId && e.listType) {
			let n = e.listId;
			if (n) {
				let r = e.listType, i = e.listStyle, a = {
					type: H.LIST,
					value: "",
					listId: n,
					listType: r,
					listStyle: i
				}, s = [];
				for (; c < o.length;) {
					let e = o[c];
					if (!e.listId || r !== e.listType) {
						c--;
						break;
					}
					delete e.listType, delete e.listStyle, s.push(e), c++;
				}
				a.valueList = X(s, {
					...t,
					isListValue: !0
				}), e = a;
			}
		} else if (e.type === H.TABLE) {
			if (e.trList) for (let n = 0; n < e.trList.length; n++) {
				let r = e.trList[n];
				delete r.id;
				for (let e = 0; e < r.tdList.length; e++) {
					let n = r.tdList[e], i = {
						colspan: n.colspan,
						rowspan: n.rowspan,
						value: X(n.value, {
							...t,
							isClassifyArea: !0
						})
					};
					Me.forEach((e) => {
						let t = n[e];
						t !== void 0 && (i[e] = t);
					}), r.tdList[e] = i;
				}
			}
		} else if (e.type === H.HYPERLINK) {
			let n = e.hyperlinkId;
			if (n) {
				let r = {
					type: H.HYPERLINK,
					value: "",
					url: e.url
				}, i = [];
				for (; c < o.length;) {
					let e = o[c];
					if (n !== e.hyperlinkId) {
						c--;
						break;
					}
					delete e.type, delete e.url, i.push(e), c++;
				}
				r.valueList = X(i, t), e = r;
			}
		} else if (e.type === H.DATE) {
			let n = e.dateId;
			if (n) {
				let r = {
					type: H.DATE,
					value: "",
					dateFormat: e.dateFormat
				}, i = [];
				for (; c < o.length;) {
					let e = o[c];
					if (n !== e.dateId) {
						c--;
						break;
					}
					delete e.type, delete e.dateFormat, i.push(e), c++;
				}
				r.valueList = X(i, t), e = r;
			}
		} else if (e.controlId) {
			let r = e.controlId;
			if (e.controlComponent === K.PREFIX) {
				let i = [], a = !1, s = c;
				for (; s < o.length;) {
					let e = o[s];
					if (e.controlId === r) {
						if (e.controlComponent === K.VALUE && (delete e.control, delete e.controlId, i.push(e)), e.controlComponent === K.POSTFIX) {
							a = !0, s++;
							break;
						}
						s++;
						continue;
					}
					if (e.controlComponent === K.PREFIX) {
						let n = s;
						for (; n < o.length;) {
							let t = o[n];
							if (t.controlId === e.controlId && t.controlComponent === K.POSTFIX) break;
							n++;
						}
						let r = X(o.slice(s, Math.min(n + 1, o.length)), t)[0];
						r && i.push(r), s = n + 1;
						continue;
					}
					break;
				}
				if (a) {
					let a = V(e, Le), o = {
						...e.control,
						...a
					}, l = {
						...V(e, Ee),
						type: H.CONTROL,
						value: "",
						control: o,
						controlId: r,
						trace: e.trace
					};
					l.control.value = X(i, t), e = xn(l, { extraPickAttrs: n }), c += s - c - 1;
				}
			}
			if (e.controlComponent && (delete e.control, delete e.controlId, e.controlComponent !== K.VALUE && e.controlComponent !== K.PRE_TEXT && e.controlComponent !== K.POST_TEXT)) {
				c++;
				continue;
			}
		}
		let i = xn(e, { extraPickAttrs: n });
		if (!e.type || e.type === H.TEXT || e.type === H.SUBSCRIPT || e.type === H.SUPERSCRIPT) for (; c < o.length;) {
			let e = o[c + 1];
			if (c++, e && bn(i, xn(e, { extraPickAttrs: n }))) {
				let t = e.value === "​" ? "\n" : e.value;
				i.value += t;
			} else break;
		}
		else c++;
		s.push(i);
	}
	return s;
}
function Sn(e) {
	switch (window.getComputedStyle(e).textAlign) {
		case "left":
		case "start": return u.LEFT;
		case "center": return u.CENTER;
		case "right":
		case "end": return u.RIGHT;
		case "justify": return u.ALIGNMENT;
		case "justify-all": return u.JUSTIFY;
		default: return u.LEFT;
	}
}
function Cn(e) {
	return e === u.ALIGNMENT ? "justify" : e;
}
function wn(e) {
	switch (e) {
		case u.LEFT: return "flex-start";
		case u.CENTER: return "center";
		case u.RIGHT: return "flex-end";
		case u.ALIGNMENT:
		case u.JUSTIFY: return "space-between";
		default: return "flex-start";
	}
}
function Tn(e) {
	return !e.type || Be.includes(e.type);
}
function En(e) {
	return !e.type || e.type === H.TEXT;
}
function Dn(e) {
	return e.filter((e) => Tn(e)).map((e) => e.value).join("").replace(/* @__PURE__ */ RegExp("​", "g"), "");
}
function On(e, t) {
	let n = e[t];
	if (!n) return null;
	let r = e[t + 1];
	return !n.listId && n.value === "​" && r && r.value !== "​" && n.areaId === r.areaId ? r : n;
}
function kn(e, t, n, r) {
	let i = On(e, n);
	if (!i) return;
	let { isBreakWhenWrap: a = !1, editorOptions: o, ignoreContextKeys: s = [] } = r || {}, { mode: c } = o || {};
	c !== p.DESIGN && i.title?.disabled && (i = ae(i, Pe));
	let l = !1;
	for (let o = 0; o < t.length; o++) {
		let c = t[o];
		if (a && !i.listId && C.test(c.value) && (l = !0), l || !i.listId && c.type === H.LIST) {
			let e = [
				...Ne,
				...Ee,
				...Re
			];
			ie(e, s), B(e, i, c), c.valueList?.forEach((t) => {
				B(e, i, t);
			});
			continue;
		}
		c.valueList?.length && kn(e, c.valueList, n, r);
		let u = [...ze];
		Rn(c) || u.push(...Ee), ie(u, s), B(u, i, c);
	}
}
function An(e, t) {
	let n = "span";
	e.type === H.SUPERSCRIPT ? n = "sup" : e.type === H.SUBSCRIPT && (n = "sub");
	let r = document.createElement(n);
	return r.style.fontFamily = e.font || t.defaultFont, e.rowFlex && (r.style.textAlign = Cn(e.rowFlex)), e.color && (r.style.color = e.color), e.bold && (r.style.fontWeight = "600"), e.italic && (r.style.fontStyle = "italic"), r.style.fontSize = `${e.size || t.defaultSize}px`, e.highlight && (r.style.backgroundColor = e.highlight), e.underline && (r.style.textDecoration = "underline", r.style.textDecorationStyle = e.textDecoration?.style || "solid"), e.strikeout && (r.style.textDecoration += " line-through"), e.type && r.setAttribute("data-type", e.type), e.rowMargin && (r.style.lineHeight = (e.rowMargin ?? t.defaultRowMargin).toString()), r.innerText = e.value.replace(/* @__PURE__ */ RegExp("​", "g"), "\n"), r;
}
function jn(e) {
	let t = 0, n = /* @__PURE__ */ new Map();
	for (let r = 0; r < e.length; r++) {
		let i = e[r];
		if (r === 0) {
			if (i.checkbox) continue;
			i.value = i.value.replace(C, "");
		}
		if (i.listWrap) {
			let e = n.get(t) || [];
			e.push(i), n.set(t, e);
		} else {
			let e = i.value.split("\n");
			for (let r = 0; r < e.length; r++) {
				r > 0 && (t += 1);
				let a = e[r], o = n.get(t) || [];
				o.push({
					...i,
					value: a
				}), n.set(t, o);
			}
		}
	}
	return n;
}
function Mn(e) {
	let t = [];
	if (!e.length) return t;
	let n = e[0]?.rowFlex || null;
	t.push({
		rowFlex: n,
		data: [e[0]]
	});
	for (let r = 1; r < e.length; r++) {
		let i = e[r], a = i.rowFlex || null;
		n === a && !Rn(i) && !Rn(e[r - 1]) ? t[t.length - 1].data.push(i) : (t.push({
			rowFlex: a,
			data: [i]
		}), n = a);
	}
	for (let e = 0; e < t.length; e++) {
		let n = t[e];
		n.data = X(n.data);
	}
	return t;
}
function Nn(e, t) {
	let n = mn(t);
	function r(e) {
		let i = document.createElement("div");
		for (let a = 0; a < e.length; a++) {
			let s = e[a];
			if (s.type === H.TABLE) {
				let e = document.createElement("table");
				e.setAttribute("cellSpacing", "0"), e.setAttribute("cellpadding", "0"), e.setAttribute("border", "0");
				let n = "1px solid #000000";
				!s.borderType || s.borderType === kt.ALL ? (e.style.borderTop = n, e.style.borderLeft = n) : s.borderType === kt.EXTERNAL && (e.style.border = n), e.style.width = `${s.width}px`;
				let r = document.createElement("colgroup");
				for (let e = 0; e < s.colgroup.length; e++) {
					let t = s.colgroup[e], n = document.createElement("col");
					n.setAttribute("width", `${t.width}`), r.append(n);
				}
				e.append(r);
				let a = s.trList;
				for (let r = 0; r < a.length; r++) {
					let i = document.createElement("tr"), o = a[r];
					i.style.height = `${o.height}px`;
					for (let e = 0; e < o.tdList.length; e++) {
						let r = document.createElement("td");
						(!s.borderType || s.borderType === kt.ALL) && (r.style.borderBottom = r.style.borderRight = "1px solid");
						let a = o.tdList[e];
						r.colSpan = a.colspan, r.rowSpan = a.rowspan, r.style.verticalAlign = a.verticalAlign || "top", a.borderTypes?.includes(At.TOP) && (r.style.borderTop = n), a.borderTypes?.includes(At.RIGHT) && (r.style.borderRight = n), a.borderTypes?.includes(At.BOTTOM) && (r.style.borderBottom = n), a.borderTypes?.includes(At.LEFT) && (r.style.borderLeft = n), r.innerHTML = Nn(a.value, t).innerHTML, a.backgroundColor && (r.style.backgroundColor = a.backgroundColor), i.append(r);
					}
					e.append(i);
				}
				i.append(e);
			} else if (s.type === H.HYPERLINK) {
				let e = document.createElement("a");
				e.innerText = s.valueList.map((e) => e.value).join(""), s.url && (e.href = s.url), i.append(e);
			} else if (s.type === H.TITLE) {
				let e = document.createElement(`h${wt[s.level]}`);
				e.innerHTML = r(s.valueList).innerHTML, i.append(e);
			} else if (s.type === H.LIST) {
				let e = document.createElement(bt[s.listType]);
				s.listStyle && (e.style.listStyleType = xt[s.listStyle]), jn(X(s.valueList)).forEach((t) => {
					let n = document.createElement("li");
					n.innerHTML = r(t).innerHTML, e.append(n);
				}), i.append(e);
			} else if (s.type === H.IMAGE) {
				let e = document.createElement("img");
				s.value && (e.src = s.value, e.width = s.width, e.height = s.height), i.append(e);
			} else if (s.type === H.BLOCK) {
				if (s.block?.type === Et.VIDEO) {
					let e = s.block.videoBlock?.src;
					if (e) {
						let n = document.createElement("video");
						n.style.display = "block", n.controls = !0, n.src = e, n.width = s.width || t?.width || window.innerWidth, n.height = s.height, i.append(n);
					}
				} else if (s.block?.type === Et.IFRAME) {
					let { src: e, srcdoc: n, sandbox: r, allow: a } = s.block.iframeBlock || {};
					if (e || n) {
						let o = document.createElement("iframe");
						o.sandbox.add(...r || Ge.sandbox), o.setAttribute("allow", [a || Ge.allow].join(" ")), o.style.display = "block", o.style.border = "none", e ? o.src = e : n && (o.srcdoc = n), o.width = `${s.width || t?.width || window.innerWidth}`, o.height = `${s.height}`, i.append(o);
					}
				}
			} else if (s.type === H.SEPARATOR) {
				let e = document.createElement("hr");
				s.dashArray?.length && e.setAttribute("data-dash-array", s.dashArray.join(",")), i.append(e);
			} else if (s.type === H.CHECKBOX) {
				let e = document.createElement("input");
				e.type = "checkbox", s.checkbox?.value && e.setAttribute("checked", "true"), i.append(e);
			} else if (s.type === H.RADIO) {
				let e = document.createElement("input");
				e.type = "radio", s.radio?.value && e.setAttribute("checked", "true"), i.append(e);
			} else if (s.type === H.TAB) {
				let e = document.createElement("span");
				e.innerHTML = `${o}${o}`, i.append(e);
			} else if (s.type === H.CONTROL) {
				let e = document.createElement("span");
				e.innerHTML = r(s.control?.value || []).innerHTML, i.append(e);
			} else if (s.type === H.PAGE_BREAK) {
				let e = document.createElement("div");
				e.style.breakAfter = "page", i.append(e);
			} else if (!s.type || s.type === H.LATEX || Be.includes(s.type)) {
				let t = "";
				if (t = s.type === H.DATE ? s.valueList?.map((e) => e.value).join("") || "" : s.value, !t) continue;
				let r = An(s, n);
				e[a - 1]?.type === H.TITLE && (t = t.replace(/^\n/, "")), r.innerText = t.replace(/* @__PURE__ */ RegExp("​", "g"), "\n"), i.append(r);
			}
		}
		return i;
	}
	let i = document.createElement("div"), a = Mn(e);
	for (let e = 0; e < a.length; e++) {
		let t = a[e], n = !t.rowFlex || t.rowFlex === u.LEFT, o = document.createElement("div");
		if (!n) {
			let e = t.data[0];
			Rn(e) ? (o.style.display = "flex", o.style.justifyContent = wn(e.rowFlex)) : (o.style.textAlign = Cn(t.rowFlex), t.rowFlex === "justify" && (o.style.textAlignLast = "justify"));
		}
		o.innerHTML = r(t.data).innerHTML, n ? o.childNodes.forEach((e) => {
			i.append(e.cloneNode(!0));
		}) : i.append(o);
	}
	return i;
}
function Pn(e) {
	if (!e || e.nodeType !== 3) return null;
	let t = e.parentNode, n = t.nodeName === "FONT" ? t.parentNode : t, r = Sn(n), i = e.textContent, a = window.getComputedStyle(n);
	if (!i || n.nodeName === "STYLE") return null;
	let o = {
		value: i,
		color: a.color,
		bold: Number(a.fontWeight) > 500,
		italic: a.fontStyle.includes("italic"),
		size: Math.floor(parseFloat(a.fontSize))
	};
	return n.nodeName === "SUB" || a.verticalAlign === "sub" ? o.type = H.SUBSCRIPT : (n.nodeName === "SUP" || a.verticalAlign === "super") && (o.type = H.SUPERSCRIPT), r !== u.LEFT && (o.rowFlex = r), a.backgroundColor !== "rgba(0, 0, 0, 0)" && (o.highlight = a.backgroundColor), a.textDecorationLine.includes("underline") && (o.underline = !0), a.textDecorationLine.includes("line-through") && (o.strikeout = !0), o;
}
function Fn(e, t) {
	let n = [];
	function r(e) {
		if (e.nodeType === 3) {
			let t = Pn(e);
			t && n.push(t);
		} else if (e.nodeType === 1) {
			let i = e.childNodes;
			for (let e = 0; e < i.length; e++) {
				let a = i[e];
				if (a.nodeName === "BR") n.push({ value: "\n" });
				else if (a.nodeName === "A") {
					let e = a, t = e.innerText;
					t && n.push({
						type: H.HYPERLINK,
						value: "",
						valueList: [{ value: t }],
						url: e.href
					});
				} else if (/H[1-6]/.test(a.nodeName)) {
					let e = Fn(zn(a, "div").outerHTML, t);
					n.push({
						value: "",
						type: H.TITLE,
						level: Tt[a.nodeName],
						valueList: e
					}), a.nextSibling && !Ue.includes(a.nextSibling.nodeName) && n.push({ value: "\n" });
				} else if (a.nodeName === "UL" || a.nodeName === "OL") {
					let e = a, r = {
						value: "",
						type: H.LIST,
						valueList: []
					};
					a.nodeName === "OL" ? r.listType = mt.OL : (r.listType = mt.UL, r.listStyle = e.style.listStyleType);
					let i = (e, n) => {
						let r = M(), a = e.tagName === "OL" ? mt.OL : mt.UL, o = e.tagName === "OL" ? void 0 : e.style.listStyleType, s = [];
						return Array.from(e.children).forEach((e) => {
							let c = e;
							if (c.tagName !== "LI") return;
							let l = c.cloneNode(!0);
							l.querySelectorAll("ul,ol").forEach((e) => e.remove());
							let u = Fn(l.innerHTML, t);
							u.forEach((e) => {
								e.value === "\n" && (e.listWrap = !0), e.listId = r, e.listType = a, o && (e.listStyle = o), e.listLevel = n;
							}), u.unshift({
								value: "\n",
								listId: r,
								listType: a,
								...o ? { listStyle: o } : {},
								listLevel: n
							}), s.push(...u), Array.from(c.querySelectorAll(":scope > ul, :scope > ol")).forEach((e) => {
								s.push(...i(e, n + 1));
							});
						}), s;
					};
					r.valueList = i(e, 0), n.push(r);
				} else if (a.nodeName === "HR") n.push({
					value: "\n",
					type: H.SEPARATOR
				});
				else if (a.nodeName === "IMG") {
					let { src: e, width: t, height: r } = a;
					e && t && r && n.push({
						width: t,
						height: r,
						value: e,
						type: H.IMAGE,
						rowFlex: Sn(a.parentElement)
					});
				} else if (a.nodeName === "VIDEO") {
					let { src: e, width: t, height: r } = a;
					e && t && r && n.push({
						value: "",
						type: H.BLOCK,
						block: {
							type: Et.VIDEO,
							videoBlock: { src: e }
						},
						width: t,
						height: r
					});
				} else if (a.nodeName === "IFRAME") {
					let { src: e, srcdoc: t, width: r, height: i } = a;
					(e || t) && r && i && n.push({
						value: "",
						type: H.BLOCK,
						block: {
							type: Et.IFRAME,
							iframeBlock: {
								src: e,
								srcdoc: t
							}
						},
						width: parseInt(r),
						height: parseInt(i)
					});
				} else if (a.nodeName === "TABLE") {
					let e = a, r = {
						type: H.TABLE,
						value: "\n",
						colgroup: [],
						trList: []
					}, i = e.querySelectorAll("colgroup col");
					if (e.querySelectorAll("tr").forEach((e) => {
						let n = Number(window.getComputedStyle(e).height.replace("px", "")), i = {
							height: n,
							minHeight: n,
							tdList: []
						};
						e.querySelectorAll("th,td").forEach((e) => {
							let n = e, r = Fn(n.innerHTML, t), a = {
								colspan: n.colSpan,
								rowspan: n.rowSpan,
								value: r,
								verticalAlign: window.getComputedStyle(e).verticalAlign,
								width: parseFloat(window.getComputedStyle(e).width)
							};
							n.style.backgroundColor && (a.backgroundColor = n.style.backgroundColor), i.tdList.push(a);
						}), r.trList.push(i);
					}), r.trList.length) {
						let e = r.trList[0].tdList.reduce((e, t) => e + t.colspan, 0), a = Math.ceil(t.innerWidth / e);
						for (let t = 0; t < e; t++) {
							let e = i[t]?.getAttribute("width");
							r.colgroup.push({ width: e ? parseFloat(e) : a });
						}
						n.push(r);
					}
				} else if (a.nodeName === "INPUT" && a.type === K.CHECKBOX) n.push({
					type: H.CHECKBOX,
					value: "",
					checkbox: { value: a.checked }
				});
				else if (a.nodeName === "INPUT" && a.type === K.RADIO) n.push({
					type: H.RADIO,
					value: "",
					radio: { value: a.checked }
				});
				else if (r(a), a.nodeType === 1 && e !== i.length - 1) {
					let e = a;
					window.getComputedStyle(e).display === "block" && !/(\n|\r\n)$/.test(e.textContent) && n.push({ value: "\n" });
				}
			}
		}
	}
	let i = document.createElement("div");
	document.body.appendChild(i);
	let a = i.attachShadow({ mode: "open" }), o = document.createElement("div");
	o.innerHTML = e, a.appendChild(o);
	let s = [];
	return o.childNodes.forEach((e) => {
		e.nodeType !== 1 && !e.textContent?.trim() && s.push(e);
	}), s.forEach((e) => e.remove()), r(o), i.remove(), n;
}
function In(e, t = {}) {
	function n(e) {
		let t = "";
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			if (i.type === H.TABLE) {
				t += "\n";
				let e = i.trList;
				for (let r = 0; r < e.length; r++) {
					let i = e[r];
					for (let e = 0; e < i.tdList.length; e++) {
						let r = i.tdList[e], a = n(X(r.value, { isClone: !1 })), o = e === 0, s = i.tdList.length - 1 === e;
						t += `${o ? "" : "  "}${a}${s ? "\n" : ""}`;
					}
				}
			} else if (i.type === H.TAB) t += "	";
			else if (i.type === H.HYPERLINK) t += i.valueList.map((e) => e.value).join("");
			else if (i.type === H.TITLE) t += `${n(X(i.valueList, { isClone: !1 }))}`;
			else if (i.type === H.LIST) {
				let e = jn(X(i.valueList, { isClone: !1 })), r = "";
				i.listType === mt.UL && (r = yt[i.listStyle]), e.forEach((i, a) => {
					let o = e.size - 1 === a;
					t += `\n${r || `${a + 1}.`}${n(i)}${o ? "\n" : ""}`;
				});
			} else if (i.type === H.CHECKBOX) t += i.checkbox?.value ? "☑" : "□";
			else if (i.type === H.RADIO) t += i.radio?.value ? "☉" : "○";
			else if (!i.type || i.type === H.LATEX || Be.includes(i.type)) {
				let e = "";
				if (i.type === H.CONTROL) {
					let t = i.control.value?.[0]?.value || "";
					e = t ? `${i.control?.preText || ""}${t}${i.control?.postText || ""}` : "";
				} else e = i.type === H.DATE ? i.valueList?.map((e) => e.value).join("") || "" : i.value;
				t += e.replace(/* @__PURE__ */ RegExp("​", "g"), "\n");
			}
		}
		return t;
	}
	return n(X(e, { isClone: t.isClone !== !1 }));
}
function Ln(e) {
	return O(e, ["metrics", "style"]);
}
function Rn(e) {
	return !!e?.type && (He.includes(e.type) || e.imgDisplay === r.INLINE);
}
function zn(e, t) {
	let n = document.createElement(t);
	for (let t = 0; t < e.attributes.length; t++) {
		let r = e.attributes[t];
		n.setAttribute(r.name, r.value);
	}
	return n.innerHTML = e.innerHTML, n;
}
function Bn(e) {
	let t = [];
	for (let n = 0; n < e.length; n++) {
		let i = e[n];
		i.imgDisplay === r.SURROUND && t.push(i);
	}
	return t;
}
function Vn(e, t) {
	for (let n = e.length - 1; n >= 0; n--) e[n].imgFloatPosition?.pageNo === t && e.splice(n, 1);
}
function Hn(e, t, n = i.BEFORE, r) {
	if (!e[t]?.hide && !e[t]?.control?.hide && !e[t]?.area?.hide && !r?.(e[t])) return t;
	let a = t;
	if (n === i.BEFORE) for (a = t - 1; a > 0;) {
		if (!e[a]?.hide && !e[a]?.control?.hide && !e[a]?.area?.hide && !r?.(e[a])) return a;
		a--;
	}
	else for (a = t + 1; a < e.length;) {
		if (!e[a]?.hide && !e[a]?.control?.hide && !e[a]?.area?.hide && !r?.(e[a])) return a;
		a++;
	}
	return a;
}
function Un(e, t, n, r) {
	let i = t + n;
	if (i < 0 || i >= e.length || e[i].controlId === r) return i;
	for (; i >= 0 && i < e.length;) {
		if (e[i].controlId === r) return i;
		i += n;
	}
	return i;
}
function Wn(e, t) {
	let n = e[t]?.controlId;
	if (!n) return null;
	let r = t;
	for (; r > 0;) {
		let t = e[r];
		if (t.controlId !== n || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) break;
		r--;
	}
	let i = e[r - 1]?.controlId;
	return i && i !== n ? Wn(e, r - 1) : n;
}
function Gn(e, t) {
	for (let n of e) {
		if (t(n), n.type === H.TABLE) for (let e of n.trList || []) for (let n of e.tdList) Gn(n.value, t);
		n.valueList && Gn(n.valueList, t);
	}
}
//#endregion
//#region src/editor/utils/clipboard.ts
function Kn(e) {
	localStorage.setItem(ve, JSON.stringify({
		text: e.text,
		elementList: e.elementList
	}));
}
function qn() {
	let e = localStorage.getItem(ve);
	return e ? JSON.parse(e) : null;
}
function Jn() {
	localStorage.removeItem(ve);
}
async function Yn(e, t, n) {
	if (!e && !t && !n.length) return;
	let r = new Blob([e], { type: "text/plain" }), i = new Blob([t], { type: "text/html" });
	if (window.ClipboardItem) {
		let e = new ClipboardItem({
			[r.type]: r,
			[i.type]: i
		});
		await window.navigator.clipboard.write([e]);
	} else {
		let e = document.createElement("div");
		e.setAttribute("contenteditable", "true"), e.innerHTML = t, document.body.append(e);
		let n = window.getSelection(), r = document.createRange(), i = document.createElement("span");
		i.innerText = "\n", e.append(i), r.selectNodeContents(e), n?.removeAllRanges(), n?.addRange(r), document.execCommand("copy"), e.remove();
	}
	Kn({
		text: e,
		elementList: n
	});
}
async function Xn(e, t) {
	let n = gn(e), r = Nn(n, t);
	document.body.append(r);
	let i = r.innerText;
	r.remove();
	let a = r.innerHTML;
	!i && !a && !n.length || await Yn(i, a, X(n, { isClone: !1 }));
}
function Zn(e) {
	let t = !1;
	for (let n = 0; n < e.items.length; n++) if (e.items[n].kind === "file") {
		t = !0;
		break;
	}
	return t;
}
//#endregion
//#region src/editor/core/event/handlers/paste.ts
function Qn(e, t) {
	let n = e.getDraw();
	if (n.isReadonly() || n.isDisabled() || n.getControl().getIsDisabledPasteControl()) return;
	let r = n.getRange(), { startIndex: i } = r.getRange(), a = n.getElementList();
	if (~i && !r.getIsSelectAll()) {
		let e = a[i];
		if (e?.titleId || e?.listId) {
			let n = 0;
			for (; n < t.length;) {
				let r = t[n];
				if (e.titleId && /^\n/.test(r.value)) break;
				if (We.includes(r.type)) {
					if (t.splice(n, 1), r.valueList) for (let e = 0; e < r.valueList.length; e++) {
						let i = r.valueList[e];
						i.value !== "​" && i.value !== "\n" && (t.splice(n, 0, i), n++);
					}
					n--;
				}
				n++;
			}
		}
		kn(a, t, i, {
			isBreakWhenWrap: !0,
			editorOptions: n.getOptions()
		});
	}
	Gn(t, (e) => {
		delete e.trace;
	}), n.insertElementList(t);
}
function $n(e, t) {
	let n = e.getDraw();
	n.isReadonly() || n.isDisabled() || Qn(e, Fn(t, { innerWidth: n.getOriginalInnerWidth() }));
}
function er(e, t) {
	let n = e.getDraw();
	if (n.isReadonly() || n.isDisabled()) return;
	let { pasteImage: r } = n.getOverride();
	if (r && r(t)?.preventDefault !== !1) return;
	let { startIndex: i } = n.getRange().getRange(), a = n.getElementList(), o = new FileReader();
	o.readAsDataURL(t), o.onload = () => {
		let e = new Image(), t = o.result;
		e.src = t, e.onload = () => {
			let r = {
				value: t,
				type: H.IMAGE,
				width: e.width,
				height: e.height
			};
			~i && kn(a, [r], i, { editorOptions: n.getOptions() }), n.insertElementList([r]);
		};
	};
}
function tr(e, t) {
	let n = e.getDraw();
	if (n.isReadonly() || n.isDisabled()) return;
	let r = t.clipboardData;
	if (!r) return;
	let { paste: i } = n.getOverride();
	if (i && i(t)?.preventDefault !== !1) return;
	if (!Zn(r)) {
		let t = r.getData("text"), n = qn();
		if (n && pe(t) === pe(n.text)) {
			Qn(e, n.elementList);
			return;
		}
	}
	Jn();
	let a = !1;
	for (let e = 0; e < r.items.length; e++) if (r.items[e].type === "text/html") {
		a = !0;
		break;
	}
	for (let t = 0; t < r.items.length; t++) {
		let n = r.items[t];
		if (n.kind === "string") {
			if (n.type === "text/plain" && !a) {
				n.getAsString((t) => {
					e.input(t);
				});
				break;
			}
			if (n.type === "text/html" && a) {
				n.getAsString((t) => {
					$n(e, t);
				});
				break;
			}
		} else if (n.kind === "file" && n.type.includes("image")) {
			let t = n.getAsFile();
			t && er(e, t);
		}
	}
}
async function nr(e, t) {
	let n = e.getDraw();
	if (n.isReadonly() || n.isDisabled()) return;
	let { paste: r } = n.getOverride();
	if (r && r()?.preventDefault !== !1) return;
	let i = await navigator.clipboard.readText(), a = qn();
	if (a && pe(i) === pe(a.text)) {
		Qn(e, a.elementList);
		return;
	}
	if (Jn(), t?.isPlainText) i && e.input(i);
	else {
		let t = await navigator.clipboard.read(), n = !1;
		for (let e of t) if (e.types.includes("text/html")) {
			n = !0;
			break;
		}
		for (let r of t) if (r.types.includes("text/plain") && !n) {
			let t = await (await r.getType("text/plain")).text();
			t && e.input(t);
		} else if (r.types.includes("text/html") && n) {
			let t = await (await r.getType("text/html")).text();
			t && $n(e, t);
		} else if (r.types.some((e) => e.startsWith("image/"))) {
			let t = r.types.find((e) => e.startsWith("image/"));
			er(e, await r.getType(t));
		}
	}
}
//#endregion
//#region src/editor/core/cursor/CursorAgent.ts
var rr = class {
	draw;
	container;
	agentCursorDom;
	canvasEvent;
	eventBus;
	constructor(e, t) {
		this.draw = e, this.container = e.getContainer(), this.canvasEvent = t, this.eventBus = e.getEventBus();
		let n = document.createElement("textarea");
		n.autocomplete = "off", n.classList.add("ce-inputarea"), n.innerText = "", this.container.append(n), this.agentCursorDom = n, n.onkeydown = (e) => this._keyDown(e), n.oninput = this._input.bind(this), n.onpaste = (e) => this._paste(e), n.addEventListener("compositionstart", this._compositionstart.bind(this)), n.addEventListener("compositionend", this._compositionend.bind(this));
	}
	getAgentCursorDom() {
		return this.agentCursorDom;
	}
	_keyDown(e) {
		this.canvasEvent.keydown(e);
	}
	_input(e) {
		let t = e.data;
		t && this.canvasEvent.input(t), this.eventBus.isSubscribe("input") && this.eventBus.emit("input", e);
	}
	_paste(e) {
		this.draw.isReadonly() || e.clipboardData && (tr(this.canvasEvent, e), e.preventDefault());
	}
	_compositionstart() {
		this.canvasEvent.compositionstart();
	}
	_compositionend(e) {
		this.canvasEvent.compositionend(e);
	}
}, ir = class {
	ANIMATION_CLASS = "ce-cursor--animation";
	draw;
	container;
	options;
	position;
	cursorDom;
	cursorAgent;
	blinkTimeout;
	hitLineStartIndex;
	constructor(e, t) {
		this.draw = e, this.container = e.getContainer(), this.position = e.getPosition(), this.options = e.getOptions(), this.cursorDom = document.createElement("div"), this.cursorDom.classList.add("ce-cursor"), this.container.append(this.cursorDom), this.cursorAgent = new rr(e, t), this.blinkTimeout = null;
	}
	getCursorDom() {
		return this.cursorDom;
	}
	getAgentDom() {
		return this.cursorAgent.getAgentCursorDom();
	}
	getAgentIsActive() {
		return this.getAgentDom() === document.activeElement;
	}
	getAgentDomValue() {
		return this.getAgentDom().value;
	}
	clearAgentDomValue() {
		this.getAgentDom().value = "";
	}
	getHitLineStartIndex() {
		return this.hitLineStartIndex;
	}
	_blinkStart() {
		this.cursorDom.classList.add(this.ANIMATION_CLASS);
	}
	_blinkStop() {
		this.cursorDom.classList.remove(this.ANIMATION_CLASS);
	}
	_setBlinkTimeout() {
		this._clearBlinkTimeout(), this.blinkTimeout = window.setTimeout(() => {
			this._blinkStart();
		}, 500);
	}
	_clearBlinkTimeout() {
		this.blinkTimeout &&= (this._blinkStop(), window.clearTimeout(this.blinkTimeout), null);
	}
	focus() {
		if (Ce && this.draw.isReadonly()) return;
		let e = this.cursorAgent.getAgentCursorDom();
		document.activeElement !== e && (e.focus(), e.setSelectionRange(0, 0));
	}
	drawCursor(e) {
		let t = this.position.getCursorPosition();
		if (!t) return;
		let { scale: n, cursor: r } = this.options, { color: i, width: a, isShow: o = !0, isBlink: s = !0, isFocus: c = !0, hitLineStartIndex: l } = {
			...r,
			...e
		};
		this.hitLineStartIndex = l, l && (t = this.position.getPositionList()[l]);
		let { metrics: u, coordinate: { leftTop: d, rightTop: f }, ascent: p, pageNo: m } = t, h = this.draw.getZone().isMainActive() ? m : this.draw.getPageNo(), { x: g, y: _ } = this.draw.getPageOffset(h), v = 12 * n, y = Math.min(u.height / 4, v), b = u.height + y * 2, x = this.cursorAgent.getAgentCursorDom();
		c && setTimeout(() => {
			this.focus();
		});
		let S = u.boundingBoxDescent < 0 ? 0 : u.boundingBoxDescent, C = d[1] + p + S - (b - y) + _, w = (l ? d[0] : f[0]) + g;
		if (x.style.left = `${w}px`, x.style.top = `${C + b - v}px`, !o) {
			this.recoveryCursor();
			return;
		}
		let T = this.cursorDom.style.top, E = this.draw.isReadonly();
		this.cursorDom.style.width = `${a * n}px`, this.cursorDom.style.backgroundColor = i, this.cursorDom.style.left = `${w}px`, this.cursorDom.style.top = `${C}px`, this.cursorDom.style.display = E ? "none" : "block", this.cursorDom.style.height = `${b}px`, s ? this._setBlinkTimeout() : this._clearBlinkTimeout(), c && R(() => {
			this.moveCursorToVisible({
				cursorPosition: t,
				direction: parseInt(T) > C ? be.UP : be.DOWN
			});
		});
	}
	recoveryCursor() {
		this.cursorDom.style.display = "none", this._clearBlinkTimeout();
	}
	moveCursorToVisible(e) {
		let { cursorPosition: t, direction: n } = e;
		if (!t || !n) return;
		let r = this.draw.getZone().isMainActive() ? t.pageNo : this.draw.getPageNo(), { coordinate: { leftTop: i, leftBottom: a } } = t, o = se(this.container), s = {
			left: 0,
			right: 0,
			top: 0,
			bottom: 0
		}, c = o === document.documentElement;
		if (c) s.right = window.innerWidth, s.bottom = window.innerHeight;
		else {
			let { left: e, right: t, top: n, bottom: r } = o.getBoundingClientRect();
			s.left = e, s.right = t, s.top = n, s.bottom = r;
		}
		let l = this.draw.getPageOffset(r).y + this.container.getBoundingClientRect().top, u = n === be.UP, d = a[0] + (c ? 0 : s.left), f = u ? i[1] + l : a[1] + l, { maskMargin: p } = this.options;
		if (s.top += p[0], s.bottom -= p[2], !(d >= s.left && d <= s.right && f >= s.top && f <= s.bottom)) {
			let { scrollLeft: e, scrollTop: t } = o;
			u ? o.scroll(e, t - (s.top - f)) : o.scroll(e, t + f - s.bottom);
		}
	}
}, ar;
(function(e) {
	e[e.LEFT = 0] = "LEFT", e[e.CENTER = 1] = "CENTER", e[e.RIGHT = 2] = "RIGHT";
})(ar ||= {});
//#endregion
//#region src/editor/utils/hotkey.ts
function or(e) {
	return xe ? e.metaKey : e.ctrlKey;
}
//#endregion
//#region src/editor/dataset/enum/KeyMap.ts
var Z;
(function(e) {
	e.Delete = "Delete", e.Backspace = "Backspace", e.ALT = "Alt", e.Enter = "Enter", e.Left = "ArrowLeft", e.Right = "ArrowRight", e.Up = "ArrowUp", e.Down = "ArrowDown", e.Home = "Home", e.End = "End", e.ESC = "Escape", e.TAB = "Tab", e.META = "Meta", e.LEFT_BRACKET = "[", e.RIGHT_BRACKET = "]", e.COMMA = ",", e.PERIOD = ".", e.LEFT_ANGLE_BRACKET = "<", e.RIGHT_ANGLE_BRACKET = ">", e.EQUAL = "=", e.MINUS = "-", e.PLUS = "+", e.A = "a", e.B = "b", e.C = "c", e.D = "d", e.E = "e", e.F = "f", e.G = "g", e.H = "h", e.I = "i", e.J = "j", e.K = "k", e.L = "l", e.M = "m", e.N = "n", e.O = "o", e.P = "p", e.Q = "q", e.R = "r", e.S = "s", e.T = "t", e.U = "u", e.V = "v", e.W = "w", e.X = "x", e.Y = "y", e.Z = "z", e.A_UPPERCASE = "A", e.B_UPPERCASE = "B", e.C_UPPERCASE = "C", e.D_UPPERCASE = "D", e.E_UPPERCASE = "E", e.F_UPPERCASE = "F", e.G_UPPERCASE = "G", e.H_UPPERCASE = "H", e.I_UPPERCASE = "I", e.J_UPPERCASE = "J", e.K_UPPERCASE = "K", e.L_UPPERCASE = "L", e.M_UPPERCASE = "M", e.N_UPPERCASE = "N", e.O_UPPERCASE = "O", e.P_UPPERCASE = "P", e.Q_UPPERCASE = "Q", e.R_UPPERCASE = "R", e.S_UPPERCASE = "S", e.T_UPPERCASE = "T", e.U_UPPERCASE = "U", e.V_UPPERCASE = "V", e.W_UPPERCASE = "W", e.X_UPPERCASE = "X", e.Y_UPPERCASE = "Y", e.Z_UPPERCASE = "Z", e.ZERO = "0", e.ONE = "1", e.TWO = "2", e.THREE = "3", e.FOUR = "4", e.FIVE = "5", e.SIX = "6", e.SEVEN = "7", e.EIGHT = "8", e.NINE = "9";
})(Z ||= {});
//#endregion
//#region src/editor/core/draw/control/checkbox/CheckboxControl.ts
var sr = class {
	element;
	control;
	constructor(e, t) {
		this.element = e, this.control = t;
	}
	setElement(e) {
		this.element = e;
	}
	getElement() {
		return this.element;
	}
	getCode() {
		return this.element.control?.code || null;
	}
	getValue() {
		let e = this.control.getElementList(), { startIndex: t } = this.control.getRange(), n = e[t], r = [], i = t;
		for (; i > 0;) {
			let t = e[i];
			if (t.controlId !== n.controlId || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) break;
			t.controlComponent === K.VALUE && r.unshift(t), i--;
		}
		let a = t + 1;
		for (; a < e.length;) {
			let t = e[a];
			if (t.controlId !== n.controlId || t.controlComponent === K.POSTFIX || t.controlComponent === K.POST_TEXT) break;
			t.controlComponent === K.VALUE && r.push(t), a++;
		}
		return r;
	}
	setValue() {
		return -1;
	}
	setSelect(e, t = {}, n = {}) {
		if (!n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return;
		let { control: r } = this.element, i = t.elementList || this.control.getElementList(), { startIndex: a } = t.range || this.control.getRange(), o = i[a], s = a;
		for (; s > 0;) {
			let t = i[s];
			if (t.controlId !== o.controlId || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) break;
			if (t.controlComponent === K.CHECKBOX) {
				let n = t.checkbox;
				n.value = e.includes(n.code);
			}
			s--;
		}
		let c = a + 1;
		for (; c < i.length;) {
			let t = i[c];
			if (t.controlId !== o.controlId || t.controlComponent === K.POSTFIX || t.controlComponent === K.POST_TEXT) break;
			if (t.controlComponent === K.CHECKBOX) {
				let n = t.checkbox;
				n.value = e.includes(n.code);
			}
			c++;
		}
		r.code = e.join(","), this.control.repaintControl({
			curIndex: a,
			isSetCursor: !1
		}), this.control.emitControlContentChange({ context: t });
	}
	keydown(e) {
		if (this.control.getIsDisabledControl()) return null;
		let t = this.control.getRange();
		this.control.shrinkBoundary();
		let { startIndex: n, endIndex: r } = t;
		return e.key === Z.Backspace || e.key === Z.Delete ? this.control.removeControl(n) : r;
	}
	cut() {
		return -1;
	}
}, cr = class extends sr {
	setSelect(e, t = {}, n = {}) {
		if (!n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return;
		let { control: r } = this.element, i = t.elementList || this.control.getElementList(), { startIndex: a } = t.range || this.control.getRange(), o = i[a], s = a;
		for (; s > 0;) {
			let t = i[s];
			if (t.controlId !== o.controlId || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) break;
			if (t.controlComponent === K.RADIO) {
				let n = t.radio;
				n.value = e.includes(n.code);
			}
			s--;
		}
		let c = a + 1;
		for (; c < i.length;) {
			let t = i[c];
			if (t.controlId !== o.controlId || t.controlComponent === K.POSTFIX || t.controlComponent === K.POST_TEXT) break;
			if (t.controlComponent === K.RADIO) {
				let n = t.radio;
				n.value = e.includes(n.code);
			}
			c++;
		}
		r.code = e.join(","), this.control.repaintControl({
			curIndex: a,
			isSetCursor: !1
		}), this.control.emitControlContentChange({ context: t });
	}
};
//#endregion
//#region src/editor/core/event/handlers/mousedown.ts
function lr(e) {
	let t = e.getDraw(), n = t.getPosition(), r = t.getRange();
	e.isAllowDrag = !0, e.cacheRange = k(r.getRange()), e.cacheElementList = t.getElementList(), e.cachePositionList = n.getPositionList(), e.cachePositionContext = n.getPositionContext();
}
function ur(e, t) {
	let { checkbox: n, control: r } = e;
	if (!r) t.getCheckboxParticle().setSelect(e);
	else {
		let e = r?.code ? r.code.split(",") : [];
		if (n?.value) {
			let t = e.findIndex((e) => e === n.code);
			~t && e.splice(t, 1);
		} else n?.code && e.push(n.code);
		let i = t.getControl().getActiveControl();
		i instanceof sr && i.setSelect(e);
	}
}
function dr(e, t) {
	let { radio: n, control: r } = e;
	if (!r) t.getRadioParticle().setSelect(e);
	else {
		let e = n?.code ? [n.code] : [], r = t.getControl().getActiveControl();
		r instanceof cr && r.setSelect(e);
	}
}
function fr(e, t) {
	let n = t.getDraw(), i = n.isReadonly(), a = n.getRange(), o = n.getPosition(), s = a.getRange();
	if (e.button === ar.RIGHT && (s.isCrossRowCol || !a.getIsCollapsed())) return;
	if (!t.isAllowDrag && !i && s.startIndex !== s.endIndex && a.getIsPointInRange(e.offsetX, e.offsetY)) {
		lr(t);
		return;
	}
	let c = e.target.dataset.index;
	c && n.setPageNo(Number(c)), t.isAllowSelection = !0;
	let l = k(o.getPositionContext()), u = o.adjustPositionContext({
		x: e.offsetX,
		y: e.offsetY
	});
	if (!u) return;
	let { index: d, isDirectHit: f, isCheckbox: m, isRadio: h, isImage: g, isLabel: _, isTable: v, tableId: y, trIndex: b, tdIndex: x, tablePath: S, tdValueIndex: C, hitLineStartIndex: w } = u;
	t.mouseDownStartPosition = {
		...u,
		index: v ? C : d,
		x: e.offsetX,
		y: e.offsetY
	};
	let T = n.getElementList(), E = o.getPositionList(), D = v ? C : d, O = T[D], A = !!(f && g), j = !!(f && m), M = !!(f && h), N = !!(f && _);
	if (~d) {
		let r = D, s = D;
		if (e.shiftKey) {
			let { startIndex: e } = a.getRange();
			~e && o.getPositionContext().tdId === l.tdId && (D > e ? r = e : s = e);
		}
		if (a.setRange(r, s), o.setCursorPosition(E[D]), i = n.isReadonly(), j && !i) ur(O, n);
		else if (M && !i) dr(O, n);
		else if (O.controlComponent === K.VALUE && (O.control?.type === G.CHECKBOX || O.control?.type === G.RADIO)) {
			let e = D;
			for (; e > 0;) {
				let t = T[e];
				if (t.controlComponent === K.CHECKBOX) {
					ur(t, n);
					break;
				}
				if (t.controlComponent === K.RADIO) {
					dr(t, n);
					break;
				}
				e--;
			}
		} else n.render({
			curIndex: D,
			isCompute: !1,
			isSubmitHistory: !1,
			isSetCursor: !A && !j && !M
		});
		w && t.getDraw().getCursor().drawCursor({ hitLineStartIndex: w });
	}
	let ee = n.getEventBus();
	N && ee.isSubscribe("labelMousedown") && ee.emit("labelMousedown", {
		evt: e,
		element: O
	});
	let P = n.getPreviewer();
	if (P.clearResizer(), A) {
		let a = { dragDisable: i || !O.controlId && n.getMode() === p.FORM };
		O.type === H.LATEX && (a.mime = "svg", a.srcKey = "laTexSVG"), P.drawResizer(O, E[D], a), n.getCursor().drawCursor({ isShow: !1 }), lr(t), (O.imgDisplay === r.SURROUND || O.imgDisplay === r.FLOAT_TOP || O.imgDisplay === r.FLOAT_BOTTOM) && n.getImageParticle().createFloatImage(O), ee.isSubscribe("imageMousedown") && ee.emit("imageMousedown", {
			evt: e,
			element: O
		});
	}
	let F = n.getTableTool();
	F.dispose(), v && !i && n.getMode() !== p.FORM && F.render();
	let I = n.getHyperlinkParticle();
	if (I.clearHyperlinkPopup(), O.type === H.HYPERLINK && (or(e) ? I.openHyperlink(O) : I.drawHyperlinkPopup(O, E[D])), n.getZone().isMainActive() && f && ee.isSubscribe("spellcheckClick")) {
		let t = v ? {
			tableId: y,
			tableIndex: d,
			trIndex: b,
			tdIndex: x,
			tablePath: S
		} : void 0, r = n.getSpellcheck().getRangeByIndex(D, t);
		r && ee.emit("spellcheckClick", {
			evt: e,
			range: r
		});
	}
	let te = n.getDateParticle();
	te.clearDatePicker(), O.type === H.DATE && !i && te.renderDatePicker(O, E[D]);
}
//#endregion
//#region src/editor/core/event/handlers/mouseup.ts
function pr(e) {
	let t = M();
	return Reflect.set(e, "dragId", t), t;
}
function mr(e, t) {
	return t.findIndex((t) => t.dragId === e);
}
function hr(e, t, n, i, a) {
	let o = n.getDraw(), s = o.getPosition();
	if (e.imgDisplay === r.SURROUND || e.imgDisplay === r.FLOAT_TOP || e.imgDisplay === r.FLOAT_BOTTOM) {
		let r = t.offsetX - n.mouseDownStartPosition.x, c = t.offsetY - n.mouseDownStartPosition.y, l = e.imgFloatPosition, u = i?.isTable, d = a.isTable, f = l.x + r, p = l.y + c, m = o.getPageNo();
		if (u && !d) {
			let e = i?.index;
			if (e !== void 0) {
				let t = s.getOriginalPositionList()[e];
				if (t) {
					let [e, n] = t.coordinate.leftTop;
					f = l.x + e + r, p = l.y + n + c;
				}
			}
		} else if (!u && d) {
			let e = a.index;
			if (e !== void 0) {
				let t = s.getOriginalPositionList()[e];
				if (t) {
					let [e, n] = t.coordinate.leftTop;
					f = l.x + r - e, p = l.y + c - n;
				}
			}
		}
		e.imgFloatPosition = {
			...l,
			x: f,
			y: p,
			pageNo: m
		};
	}
	o.getImageParticle().destroyFloatImage();
}
function gr(e, t) {
	if (t.isAllowDrop) {
		let n = t.getDraw();
		if (n.isReadonly() || n.isDisabled()) {
			t.mousedown(e);
			return;
		}
		let i = n.getPosition(), a = i.getPositionList(), o = i.getPositionContext(), s = n.getRange(), c = t.cacheRange, l = t.cacheElementList, u = t.cachePositionList, d = t.cachePositionContext, f = s.getRange(), p = c.startIndex === c.endIndex, m = p ? c.startIndex - 1 : c.startIndex, h = c.endIndex;
		if (f.startIndex >= m && f.endIndex <= h && t.cachePositionContext?.tdId === o.tdId) {
			n.clearSideEffect();
			let i = !1, a = !1;
			if (p) {
				let s = l[h];
				if (s.type === H.IMAGE || s.type === H.LATEX) {
					if (hr(s, e, t, t.cachePositionContext, o), s.imgDisplay === r.SURROUND || s.imgDisplay === r.FLOAT_TOP || s.imgDisplay === r.FLOAT_BOTTOM) n.getPreviewer().drawResizer(s), i = !0;
					else {
						let e = u[h];
						n.getPreviewer().drawResizer(s, e);
					}
					a = s.imgDisplay === r.SURROUND;
				}
			}
			s.replaceRange({ ...c }), n.render({
				isCompute: a,
				isSubmitHistory: i,
				isSetCursor: !1
			});
			return;
		}
		let g = l.slice(m + 1, h + 1), _ = g.find((e) => e.controlId);
		if (_) {
			let e = l[m + 1], t = l[h];
			if (!((!e.controlId || e.controlComponent === K.PREFIX) && (!t.controlId || t.controlComponent === K.POSTFIX) || e.controlId === t.controlId && e.controlComponent === K.PREFIX && t.controlComponent === K.POSTFIX || e.control?.type === G.TEXT && e.controlComponent === K.VALUE && t.control?.type === G.TEXT && t.controlComponent === K.VALUE)) {
				n.render({
					curIndex: f.startIndex,
					isCompute: !1,
					isSubmitHistory: !1
				});
				return;
			}
		}
		let v = n.getControl(), y = n.getElementList(), b = !_ || !!y[f.startIndex].controlId || !v.getIsElementListContainFullControl(g), x = n.getOptions(), S = g.map((e) => {
			if (!e.type || e.type === H.TEXT) {
				let t = { value: e.value }, n = [...Te];
				return b || n.push(...Ie), n.forEach((n) => {
					let r = e[n];
					r !== void 0 && (t[n] = r);
				}), t;
			}
			{
				let t = k(e);
				return b && (t = ae(t, Ie)), yn([t], {
					isHandleFirstElement: !1,
					editorOptions: x
				}), t;
			}
		});
		kn(y, S, f.startIndex, { editorOptions: n.getOptions() }), Gn(S, (e) => {
			delete e.trace;
		}), n.getTraceParticle().markElementListInserted(S);
		let C = l[m], w = u[m], T = pr(l[m]), E = pr(l[h]), D = S.length, O = f.startIndex, A = O + D, j = v.getActiveControl();
		if (j && l[O].controlComponent !== K.POSTFIX ? (A = j.setValue(S), O = A - D) : n.spliceElementList(y, O + 1, 0, S), !~A) {
			n.render({ isSetCursor: !1 });
			return;
		}
		let M = pr(y[O]), N = pr(y[A]), ee = mr(T, l), P = mr(E, l), F = l[P];
		if (F.controlId && F.controlComponent !== K.POSTFIX) s.replaceRange({
			...c,
			startIndex: ee,
			endIndex: P
		}), v.getActiveControl()?.cut();
		else {
			let e = !0;
			if (d?.isTable) {
				let { tableId: t, trIndex: r, tdIndex: i } = d;
				e = !n.getOriginalElementList().some((e) => e.id === t && e?.trList?.[r]?.tdList?.[i]?.deletable === !1);
			}
			e && n.deleteElementList(l, ee + 1, P - ee, { tdDeletable: e });
		}
		let I = y[f.startIndex], te = a[f.startIndex], L = o.index;
		L && (I.tableId && !C.tableId ? w.index < L && (L -= D) : !I.tableId && C.tableId && te.index < L && (L += D), i.setPositionContext({
			...o,
			index: L
		}));
		let ne = mr(M, y), re = mr(N, y);
		s.setRange(p ? re : ne, re, f.tableId, f.startTdIndex, f.endTdIndex, f.startTrIndex, f.endTrIndex), n.clearSideEffect();
		let R = null;
		if (p) {
			let r = n.getElementList()[re];
			(r.type === H.IMAGE || r.type === H.LATEX) && (hr(r, e, t, t.cachePositionContext, o), R = r);
		}
		if (n.render({ isSetCursor: !1 }), j ? v.emitControlContentChange() : C.controlId && v.emitControlContentChange({
			context: {
				range: c,
				elementList: l
			},
			controlElement: C
		}), R) {
			if (R.imgDisplay === r.SURROUND || R.imgDisplay === r.FLOAT_TOP || R.imgDisplay === r.FLOAT_BOTTOM) n.getPreviewer().drawResizer(R);
			else {
				let e = i.getPositionList()[re];
				n.getPreviewer().drawResizer(R, e);
			}
		}
	} else t.isAllowDrag && t.cacheRange?.startIndex !== t.cacheRange?.endIndex && t.mousedown(e);
}
//#endregion
//#region src/editor/core/event/handlers/mouseleave.ts
function _r(e, t) {
	let n = t.getDraw();
	if (n.getTraceParticle().clearTracePopup(), !n.getOptions().pageOuterSelectionDisable) return;
	let { x: r, y: i, width: a, height: o } = n.getPageContainer().getBoundingClientRect();
	e.x >= r && e.x <= r + a && e.y >= i && e.y <= i + o || t.setIsAllowSelection(!1);
}
//#endregion
//#region src/editor/core/event/handlers/mousemove.ts
function vr(e, t) {
	let n = t.getDraw();
	if (n.getTraceParticle().handleMouseMove(e), n.getHintParticle().handleMouseMove(e), t.isAllowDrag) {
		let i = e.offsetX, a = e.offsetY, { startIndex: o, endIndex: s } = t.cacheRange, c = t.cachePositionList;
		for (let e = o + 1; e <= s; e++) {
			let { coordinate: { leftTop: t, rightBottom: n } } = c[e];
			if (i >= t[0] && i <= n[0] && a >= t[1] && a <= n[1]) return;
		}
		let l = t.cacheRange?.startIndex;
		if (l) {
			let i = t.cacheElementList[l];
			i?.type === H.IMAGE && (i.imgDisplay === r.SURROUND || i.imgDisplay === r.FLOAT_TOP || i.imgDisplay === r.FLOAT_BOTTOM) && (n.getPreviewer().clearResizer(), n.getImageParticle().dragFloatImage(e.movementX, e.movementY));
		}
		t.dragover(e), t.isAllowDrop = !0;
		return;
	}
	if (!t.isAllowSelection || !t.mouseDownStartPosition) return;
	let i = e.target.dataset.index;
	i && n.setPageNo(Number(i));
	let a = n.getPosition(), o = a.getPositionByXY({
		x: e.offsetX,
		y: e.offsetY
	});
	if (!~o.index) return;
	let { index: s, isTable: c, tdValueIndex: l, tdIndex: u, trIndex: d, tableId: f, trId: p, tdId: m, tablePath: h } = o, { index: g, isTable: _, tdIndex: v, trIndex: y, tableId: b } = t.mouseDownStartPosition, x = c ? l : s, S = n.getRange();
	if (c && _ && b === f && (u !== v || d !== y)) S.setRange(x, x, f, v, u, y, d), a.setPositionContext({
		isTable: c,
		index: s,
		trIndex: d,
		tdIndex: u,
		tdId: m,
		trId: p,
		tableId: f,
		tablePath: h
	});
	else {
		let e = ~x ? x : 0;
		if ((_ || c) && b !== f) return;
		let t = g;
		if (t > e && ([t, e] = [e, t]), t === e) return;
		let r = n.getElementList(), i = r[t + 1], a = r[e];
		if (i?.controlComponent === K.PLACEHOLDER && a?.controlComponent === K.PLACEHOLDER && i.controlId === a.controlId) return;
		S.setRange(t, e);
	}
	n.render({
		isSubmitHistory: !1,
		isSetCursor: !1,
		isCompute: !1
	});
}
//#endregion
//#region src/editor/core/event/handlers/keydown/backspace.ts
function yr(e) {
	let t = e.getDraw(), n = t.getTraceParticle(), r = t.getRange(), i = r.getRange(), a = t.getElementList(), o = i.startIndex, s = a[o];
	if (!s || !s.hide && !s.control?.hide && !s.area?.hide && !n.isTraceHidden(s)) return;
	let c = !1;
	for (; o > 0;) {
		let e = a[o], r = e.hide || e.control?.hide || e.area?.hide, i = n.isTraceHidden(e);
		if (!r && !i) {
			c = !0;
			break;
		}
		let s;
		if (r ? e.controlId ? s = t.getControl().removeControl(o) : (t.spliceElementList(a, o, 1), s = o - 1) : s = e.controlId ? t.getControl().getControlStartIndex(a, o, e.controlId) - 1 : o - 1, s === null || s < 0) break;
		o = s;
	}
	if (c && o !== i.startIndex) {
		i.startIndex = o, i.endIndex = o, r.replaceRange(i);
		let e = t.getPosition(), n = e.getPositionList();
		e.setCursorPosition(n[o]);
	}
}
function br(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getRange();
	if (!r.getIsCanInput()) return;
	r.getIsCollapsed() && yr(t);
	let i = n.getControl(), { startIndex: a, endIndex: o, isCrossRowCol: s } = r.getRange(), c;
	if (s) {
		let e = n.getTableParticle().getRangeRowCol();
		if (!e) return;
		let t = !1;
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			for (let e = 0; e < i.length; e++) {
				let r = i[e];
				r.value.length > 1 && (n.deleteElementList(r.value, 1, r.value.length - 1, { tdDeletable: r.deletable !== !1 }), t = !0);
			}
		}
		c = t ? 0 : null;
	} else if (i.getActiveControl() && i.getIsRangeCanCaptureEvent()) c = i.keydown(e), c && i.emitControlContentChange();
	else {
		let t = n.getPosition().getCursorPosition();
		if (!t) return;
		let { index: i } = t, s = r.getIsCollapsed(), l = n.getElementList();
		if (s && i === 0) {
			let t = l[i];
			if (t.value === "​") {
				t.listId && (t.listLevel ? n.getListParticle().decreaseListLevel() : n.getListParticle().unsetList()), e.preventDefault();
				return;
			}
		}
		let u = l[a];
		if (s && u.value === "​" && !u.listWrap) {
			let e = r.getRangeParagraphElementList();
			if (e) {
				let t = l[a - 1];
				e.forEach((e) => {
					e.rowFlex = t?.rowFlex, e.rowMargin = t?.rowMargin;
				});
			}
		}
		let d = u.value === "​" ? l[a - 1] : u, f = l[o + 1];
		if (d?.titleId && f?.titleId && d.level === f.level && d.titleId !== f.titleId) {
			let e = d.titleId, t = f.titleId, n = o + 1;
			for (; n < l.length && l[n]?.titleId === t;) l[n].titleId = e, n++;
		}
		s ? n.deleteElementList(l, i, 1) : n.deleteElementList(l, a + 1, o - a), c = s ? i - 1 : a;
	}
	n.getGlobalEvent().setCanvasEventAbility(), c === null ? (r.setRange(a, a), n.render({
		curIndex: a,
		isSubmitHistory: !1
	})) : (r.setRange(c, c), n.render({ curIndex: c }));
}
//#endregion
//#region src/editor/core/event/handlers/keydown/delete.ts
function xr(e) {
	let t = e.getDraw(), n = t.getTraceParticle(), r = t.getRange(), i = r.getRange(), a = t.getElementList(), o = i.startIndex + 1, s = a[o];
	if (!s || !s.hide && !s.control?.hide && !s.area?.hide && !n.isTraceHidden(s)) return;
	let c = !1;
	for (; o < a.length;) {
		let e = a[o], r = e.hide || e.control?.hide || e.area?.hide, i = n.isTraceHidden(e);
		if (!r && !i) {
			c = !0;
			break;
		}
		let s;
		if (r ? e.controlId ? s = t.getControl().removeControl(o) : (t.spliceElementList(a, o, 1), s = o) : s = e.controlId ? t.getControl().getControlEndIndex(a, o, e.controlId) + 1 : o + 1, s === null || s >= a.length) break;
		o = s;
	}
	if (c && o > i.startIndex + 1) {
		i.startIndex = o - 1, i.endIndex = o - 1, r.replaceRange(i);
		let e = t.getPosition(), n = e.getPositionList();
		e.setCursorPosition(n[o - 1]);
	}
}
function Sr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getRange();
	if (!r.getIsCanInput()) return;
	let { isCrossRowCol: i } = r.getRange(), { startIndex: a, endIndex: o } = r.getRange(), s = r.getIsCollapsed(), c = n.getElementList(), l = n.getControl();
	if (s) {
		xr(t);
		let e = r.getRange();
		a = e.startIndex, o = e.endIndex;
	}
	let u;
	if (i) {
		let e = n.getTableParticle().getRangeRowCol();
		if (!e) return;
		let t = !1;
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			for (let e = 0; e < i.length; e++) {
				let r = i[e];
				r.value.length > 1 && (n.deleteElementList(r.value, 1, r.value.length - 1, { tdDeletable: r.deletable !== !1 }), t = !0);
			}
		}
		u = t ? 0 : null;
	} else if (l.getActiveControl() && l.getIsRangeWithinControl()) u = l.keydown(e), u && l.emitControlContentChange();
	else if (s && c[o + 1]?.controlId) u = l.removeControl(o + 1);
	else {
		let e = n.getPosition(), t = e.getCursorPosition();
		if (!t) return;
		let { index: i } = t, s = e.getPositionContext();
		if (s.isDirectHit && s.isImage) n.deleteElementList(c, i, 1), u = i - 1;
		else {
			let e = r.getIsCollapsed();
			if (!e) n.deleteElementList(c, a + 1, o - a);
			else {
				let e = c[i + 1];
				if (!e) return;
				if (e.value === "​" && !e.listWrap) {
					let { rowFlex: t, rowMargin: n } = c[i];
					for (let r = i + 1; r < c.length; r++) {
						let a = c[r];
						if (r > i + 1 && (a.value === "​" && !a.listWrap || a.listId !== e.listId || a.titleId !== e.titleId)) break;
						a.rowFlex = t, a.rowMargin = n;
					}
				}
				n.deleteElementList(c, i + 1, 1);
			}
			u = e ? i : a;
		}
	}
	n.getGlobalEvent().setCanvasEventAbility(), u === null ? (r.setRange(a, a), n.render({
		curIndex: a,
		isSubmitHistory: !1
	})) : (r.setRange(u, u), n.render({ curIndex: u }));
}
//#endregion
//#region src/editor/core/event/handlers/keydown/enter.ts
function Cr(e, t, n, r) {
	let i = e[n], a = e[n - 1];
	return r && n > 0 && i?.listId && i.value === "​" && a?.listId && a.listId !== i.listId ? n - 1 : t;
}
function wr(e, t, n) {
	if (!(!t.listId || t.listLevel !== void 0)) for (let r = n; r >= 0; r--) {
		let n = e[r];
		if (n.listId !== t.listId) break;
		if (n.listLevel !== void 0) {
			t.listLevel = n.listLevel;
			break;
		}
	}
}
function Tr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getRange();
	if (!r.getIsCanInput()) return;
	let { startIndex: i, endIndex: a } = r.getRange(), o = r.getIsCollapsed(), s = n.getElementList(), c = s[i], l = s[a];
	if (o && l.listId && l.value === "​" && s[a + 1]?.listId !== l.listId) {
		l.listLevel ? n.getListParticle().decreaseListLevel() : n.getListParticle().unsetList();
		return;
	}
	let u = { value: "​" };
	e.shiftKey && c.listId && (u.listWrap = !0);
	let d = Cr(s, i, a, o);
	if (kn(s, [u], d, {
		isBreakWhenWrap: !0,
		editorOptions: n.getOptions()
	}), e.shiftKey && l.areaId && l.areaId !== s[a + 1]?.areaId && (u = ae(u, Re)), !(s[i + 1]?.titleId && (!c.titleId || c.titleId !== s[i + 1]?.titleId)) && !(l.titleId && l.titleId !== s[a + 1]?.titleId)) {
		let e = r.getRangeAnchorStyle(s, d);
		if (e) {
			let t = [...Ee];
			e.controlComponent !== K.POSTFIX && t.push(...Te), t.forEach((t) => {
				let n = e[t];
				n !== void 0 && (u[t] = n);
			});
		}
	}
	wr(s, u, d);
	let f = n.getControl(), p = f.getActiveControl();
	n.getTraceParticle().markElementListInserted([u]);
	let m;
	if (p && f.getIsRangeWithinControl()) m = f.setValue([u]), f.emitControlContentChange();
	else {
		let e = n.getPosition().getCursorPosition();
		if (!e) return;
		let { index: t } = e, r = d !== i;
		if (o) {
			let e = r ? a : t + 1;
			if (n.spliceElementList(s, e, 0, [u]), l.titleId && s[e + 1]?.titleId === l.titleId) {
				let t = M(), n = e + 1;
				for (; n < s.length && s[n]?.titleId === l.titleId;) s[n].titleId = t, n++;
			}
		} else {
			let e = i + 1;
			n.deleteElementList(s, e, a - i), n.spliceElementList(s, e, 0, [u]);
		}
		m = o ? r ? a : t + 1 : i + 1;
	}
	~m && (r.setRange(m, m), n.render({ curIndex: m })), e.preventDefault();
}
//#endregion
//#region src/editor/core/event/handlers/keydown/left.ts
function Er(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getPosition(), a = r.getCursorPosition();
	if (!a) return;
	let o = r.getPositionContext(), { index: s } = a;
	if (s <= 0 && !o.isTable) return;
	let c = n.getRange(), { startIndex: l, endIndex: u } = c.getRange(), d = c.getIsCollapsed(), f = n.getElementList(), m = n.getControl();
	if (n.getMode() === p.FORM && m.getActiveControl() && (f[s]?.controlComponent === K.PREFIX || f[s]?.controlComponent === K.PRE_TEXT)) {
		m.initNextControl({ direction: be.UP });
		return;
	}
	let h = 1;
	if (xe ? e.altKey : e.ctrlKey) {
		let t = n.getLetterReg(), r = e.shiftKey && !d && l === a?.index ? u : l;
		if (t.test(f[r]?.value)) {
			let e = r - 1;
			for (; e > 0;) {
				let n = f[e];
				if (!t.test(n.value)) break;
				h++, e--;
			}
		}
	}
	let g = l - h, _ = g, v = g;
	if (e.shiftKey && a && (l === u ? v = u : l === a.index ? (_ = l, v = u - h) : (_ = g, v = u)), !e.shiftKey) {
		let e = f[l];
		if (e.type === H.TABLE) {
			let t = e.trList, i = t.length - 1, a = t[i], o = a.tdList.length - 1, s = a.tdList[o];
			r.setPositionContext({
				isTable: !0,
				index: l,
				trIndex: i,
				tdIndex: o,
				tdId: s.id,
				trId: a.id,
				tableId: e.id
			}), _ = s.value.length - 1, v = _, n.getTableTool().render();
		} else if (e.tableId && l === 0) {
			let t = n.getOriginalElementList()[o.index].trList;
			outer: for (let i = 0; i < t.length; i++) {
				let a = t[i];
				if (a.id !== e.trId) continue;
				let s = a.tdList;
				for (let a = 0; a < s.length; a++) if (s[a].id === e.tdId) {
					if (i === 0 && a === 0) r.setPositionContext({ isTable: !1 }), _ = o.index - 1, v = _, n.getTableTool().dispose();
					else {
						let s = i, c = a - 1;
						c < 0 && (s = i - 1, c = t[s].tdList.length - 1);
						let l = t[s], u = l.tdList[c];
						r.setPositionContext({
							isTable: !0,
							index: o.index,
							trIndex: s,
							tdIndex: c,
							tdId: u.id,
							trId: l.id,
							tableId: e.tableId
						}), _ = u.value.length - 1, v = _, n.getTableTool().render();
					}
					break outer;
				}
			}
		}
	}
	if (!~_ || !~v) return;
	let y = n.getTraceParticle(), b = n.getElementList();
	_ = Hn(b, _, i.BEFORE, (e) => y.isTraceHidden(e)), v = Hn(b, v, i.BEFORE, (e) => y.isTraceHidden(e)), c.setRange(_, v);
	let x = _ === v;
	if (n.render({
		curIndex: x ? _ : void 0,
		isSetCursor: x,
		isSubmitHistory: !1,
		isCompute: !1
	}), x) {
		let e = r.getPositionList(), t = e[_];
		if (t?.isLastLetter && t.value !== "​" && _ + 1 < e.length) {
			let t = e[_ + 1], r = b[_], i = b[_ + 1];
			t.value !== "​" && !Rn(i) && r.listId === i.listId && n.getCursor().drawCursor({ hitLineStartIndex: _ + 1 });
		}
	}
	e.preventDefault();
}
//#endregion
//#region src/editor/core/event/handlers/keydown/right.ts
function Dr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getPosition(), a = r.getCursorPosition();
	if (!a) return;
	let { index: o } = a, s = r.getPositionList(), c = r.getPositionContext();
	if (o > s.length - 1 && !c.isTable) return;
	let l = n.getRange(), { startIndex: u, endIndex: d } = l.getRange(), f = l.getIsCollapsed(), m = n.getElementList(), h = n.getControl();
	if (n.getMode() === p.FORM && h.getActiveControl() && (m[o + 1]?.controlComponent === K.POSTFIX || m[o + 1]?.controlComponent === K.POST_TEXT)) {
		h.initNextControl({ direction: be.DOWN });
		return;
	}
	let g = 1;
	if (xe ? e.altKey : e.ctrlKey) {
		let t = n.getLetterReg(), r = e.shiftKey && !f && u === a?.index ? d : u;
		if (t.test(m[r + 1]?.value)) {
			let e = r + 2;
			for (; e < m.length;) {
				let n = m[e];
				if (!t.test(n.value)) break;
				g++, e++;
			}
		}
	}
	let _ = d + g, v = _, y = _;
	if (e.shiftKey && a && (u === d ? v = u : u === a.index ? (v = u, y = _) : (v = u + g, y = d)), !e.shiftKey) {
		let e = m[d], t = m[d + 1];
		if (t?.type === H.TABLE) {
			let e = t.trList[0], i = e.tdList[0];
			r.setPositionContext({
				isTable: !0,
				index: d + 1,
				trIndex: 0,
				tdIndex: 0,
				tdId: i.id,
				trId: e.id,
				tableId: t.id
			}), v = 0, y = 0, n.getTableTool().render();
		} else if (e.tableId && !t) {
			let t = n.getOriginalElementList()[c.index].trList;
			outer: for (let i = 0; i < t.length; i++) {
				let a = t[i];
				if (a.id !== e.trId) continue;
				let o = a.tdList;
				for (let a = 0; a < o.length; a++) if (o[a].id === e.tdId) {
					if (i === t.length - 1 && a === o.length - 1) r.setPositionContext({ isTable: !1 }), v = c.index, y = v, m = n.getElementList(), n.getTableTool().dispose();
					else {
						let s = i, l = a + 1;
						l > o.length - 1 && (s = i + 1, l = 0);
						let u = t[s], d = u.tdList[l];
						r.setPositionContext({
							isTable: !0,
							index: c.index,
							trIndex: s,
							tdIndex: l,
							tdId: d.id,
							trId: u.id,
							tableId: e.tableId
						}), v = 0, y = v, n.getTableTool().render();
					}
					break outer;
				}
			}
		}
	}
	let b = m.length - 1;
	if (v > b || y > b) return;
	let x = n.getTraceParticle(), S = n.getElementList();
	v = Hn(S, v, i.AFTER, (e) => x.isTraceHidden(e)), y = Hn(S, y, i.AFTER, (e) => x.isTraceHidden(e)), l.setRange(v, y);
	let C = v === y;
	if (n.render({
		curIndex: C ? v : void 0,
		isSetCursor: C,
		isSubmitHistory: !1,
		isCompute: !1
	}), C) {
		let e = s[v];
		if (e?.isLastLetter && e.value !== "​" && v + 1 < s.length) {
			let e = s[v + 1], t = m[v], r = m[v + 1];
			e.value !== "​" && !Rn(r) && t.listId === r.listId && n.getCursor().drawCursor({ hitLineStartIndex: v + 1 });
		}
	}
	e.preventDefault();
}
//#endregion
//#region src/editor/core/event/handlers/keydown/tab.ts
function Or(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	e.preventDefault();
	let r = n.getControl();
	if (r.getActiveControl() && r.getIsRangeWithinControl()) {
		r.initNextControl({ direction: e.shiftKey ? be.UP : be.DOWN });
		return;
	}
	let i = n.getRange(), a = n.getElementList(), { startIndex: o, endIndex: s } = i.getRange(), c = i.getIsCollapsed(), l = a[s], u = a[s - 1];
	if (c && l?.listId && !l.listWrap && (l.value === "​" || u?.value === "​" && !u?.listWrap && u.listId === l.listId)) {
		e.shiftKey ? n.getListParticle().decreaseListLevel() : n.getListParticle().increaseListLevel();
		return;
	}
	let d = i.getRangeAnchorStyle(a, s), f = {
		...d ? V(d, Te) : null,
		type: H.TAB,
		value: ""
	};
	kn(a, [f], o, { editorOptions: n.getOptions() }), n.insertElementList([f]);
}
//#endregion
//#region src/editor/core/event/handlers/keydown/updown.ts
function kr(e) {
	let { positionList: t, index: n, isUp: r, rowNo: i, cursorX: a } = e, o = -1, s = [];
	if (r) {
		let e = n - 1;
		for (; e >= 0;) {
			let n = t[e];
			if (e--, n.rowNo !== i) {
				if (s[0] && s[0].rowNo !== n.rowNo) break;
				s.unshift(n);
			}
		}
	} else {
		let e = n + 1;
		for (; e < t.length;) {
			let n = t[e];
			if (e++, n.rowNo !== i) {
				if (s[0] && s[0].rowNo !== n.rowNo) break;
				s.push(n);
			}
		}
	}
	for (let e = 0; e < s.length; e++) {
		let t = s[e], { coordinate: { leftTop: [n], rightTop: [r] } } = t;
		if (e === s.length - 1 && (o = t.index), !(a < n || a > r)) {
			o = t.index;
			break;
		}
	}
	return o;
}
function Ar(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getPosition(), i = r.getCursorPosition();
	if (!i) return;
	let a = n.getRange(), { startIndex: o, endIndex: s } = a.getRange(), c = r.getPositionList(), l = e.key === Z.Up, u = -1, d = -1, f = r.getPositionContext();
	if (!e.shiftKey && f.isTable && (l && i.rowIndex === 0 || !l && i.rowIndex === n.getRowCount() - 1)) {
		let { index: e, trIndex: t, tdIndex: i, tableId: a } = f;
		if (l) {
			if (t === 0) r.setPositionContext({ isTable: !1 }), u = e - 1, d = u, n.getTableTool().dispose();
			else {
				let o = -1, s = -1, c = n.getOriginalElementList()[e].trList, l = c[t].tdList[i].colIndex;
				outer: for (let e = t - 1; e >= 0; e--) {
					let t = c[e].tdList;
					for (let n = 0; n < t.length; n++) {
						let r = t[n];
						if (r.colIndex === l || r.colIndex + r.colspan - 1 >= l && r.colIndex <= l) {
							o = e, s = n;
							break outer;
						}
					}
				}
				if (!~o || !~s) return;
				let f = c[o], p = f.tdList[s];
				r.setPositionContext({
					isTable: !0,
					index: e,
					trIndex: o,
					tdIndex: s,
					tdId: p.id,
					trId: f.id,
					tableId: a
				}), u = p.value.length - 1, d = u, n.getTableTool().render();
			}
		} else {
			let o = n.getOriginalElementList()[e].trList;
			if (t === o.length - 1) r.setPositionContext({ isTable: !1 }), u = e, d = u, n.getTableTool().dispose();
			else {
				let s = -1, c = -1, l = o[t].tdList[i].colIndex;
				outer: for (let e = t + 1; e < o.length; e++) {
					let t = o[e].tdList;
					for (let n = 0; n < t.length; n++) {
						let r = t[n];
						if (r.colIndex === l || r.colIndex + r.colspan - 1 >= l && r.colIndex <= l) {
							s = e, c = n;
							break outer;
						}
					}
				}
				if (!~s || !~c) return;
				let f = o[s], p = f.tdList[c];
				r.setPositionContext({
					isTable: !0,
					index: e,
					trIndex: s,
					tdIndex: c,
					tdId: p.id,
					trId: f.id,
					tableId: a
				}), u = p.value.length - 1, d = u, n.getTableTool().render();
			}
		}
	} else {
		let t = i;
		e.shiftKey && (t = o === i.index ? c[s] : c[o]);
		let { index: a, rowNo: f, rowIndex: p, coordinate: { rightTop: [m] } } = t;
		if (l && p === 0 || !l && p === n.getRowCount() - 1) return;
		let h = kr({
			positionList: c,
			index: a,
			rowNo: f,
			isUp: l,
			cursorX: m
		});
		if (h < 0) return;
		u = h, d = h, e.shiftKey && (o === s ? l ? d = s : u = o : o === i.index ? u = o : d = s);
		let g = n.getElementList()[h];
		if (g.type === H.TABLE) {
			let { scale: e } = n.getOptions(), t = n.getMargins(), i = g.trList, a = -1, o = -1, s = -1;
			if (l) outer: for (let n = i.length - 1; n >= 0; n--) {
				let r = i[n].tdList;
				for (let i = 0; i < r.length; i++) {
					let c = r[i], u = c.x * e + t[3], d = c.width * e;
					if (m >= u && m <= u + d) {
						let e = c.positionList, t = e[e.length - 1], r = kr({
							positionList: e,
							index: t.index + 1,
							rowNo: t.rowNo - 1,
							isUp: l,
							cursorX: m
						}) || t.index;
						a = n, o = i, s = r;
						break outer;
					}
				}
			}
			else outer: for (let n = 0; n < i.length; n++) {
				let r = i[n].tdList;
				for (let i = 0; i < r.length; i++) {
					let c = r[i], u = c.x * e + t[3], d = c.width * e;
					if (m >= u && m <= u + d) {
						let e = c.positionList, t = kr({
							positionList: e,
							index: -1,
							rowNo: -1,
							isUp: l,
							cursorX: m
						}) || 0;
						a = n, o = i, s = t;
						break outer;
					}
				}
			}
			if (~a && ~o && ~s) {
				let e = i[a], t = e.tdList[o];
				r.setPositionContext({
					isTable: !0,
					index: h,
					trIndex: a,
					tdIndex: o,
					tdId: t.id,
					trId: e.id,
					tableId: g.id
				}), u = s, d = u, c = r.getPositionList(), n.getTableTool().render();
			}
		}
	}
	if (!~u || !~d) return;
	u > d && ([u, d] = [d, u]), a.setRange(u, d);
	let p = u === d;
	n.render({
		curIndex: p ? u : void 0,
		isSetCursor: p,
		isSubmitHistory: !1,
		isCompute: !1
	}), p || n.getCursor().moveCursorToVisible({
		cursorPosition: c[l ? u : d],
		direction: l ? be.UP : be.DOWN
	});
}
//#endregion
//#region src/editor/core/event/handlers/keydown/home.ts
function jr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getPosition(), i = r.getCursorPosition();
	if (!i) return;
	let a = n.getRange(), { startIndex: o, endIndex: s } = a.getRange(), c = r.getPositionList(), l = i;
	e.shiftKey && o !== s && (l = o === i.index ? c[s] : c[o]);
	let { rowNo: u } = l, d = l.index;
	for (let e = l.index - 1; e >= 0 && c[e].rowNo === u; e--) d = e;
	let f = c[d].value !== "​";
	f && d--;
	let p = d, m = d;
	e.shiftKey && (o === s ? (p = d, m = o) : o === i.index ? (p = o, m = d) : (p = d, m = s)), p > m && ([p, m] = [m, p]), a.setRange(p, m);
	let h = p === m;
	n.render({
		curIndex: h ? p : void 0,
		isSetCursor: h,
		isSubmitHistory: !1,
		isCompute: !1
	}), f && n.getCursor().drawCursor({ hitLineStartIndex: d + 1 }), e.preventDefault();
}
//#endregion
//#region src/editor/core/event/handlers/keydown/end.ts
function Mr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	let r = n.getPosition(), i = r.getCursorPosition();
	if (!i) return;
	let a = n.getRange(), { startIndex: o, endIndex: s } = a.getRange(), c = r.getPositionList(), l = i;
	e.shiftKey && o !== s && (l = o === i.index ? c[s] : c[o]);
	let { rowNo: u } = l;
	n.getCursor().getHitLineStartIndex() !== void 0 && u++;
	let d = l.index;
	for (let e = l.index + 1; e < c.length && c[e].rowNo === u; e++) d = e;
	let f = d, p = d;
	e.shiftKey && (o === s || o === i.index ? (f = o, p = d) : (f = d, p = s)), f > p && ([f, p] = [p, f]), a.setRange(f, p);
	let m = f === p;
	n.render({
		curIndex: m ? f : void 0,
		isSetCursor: m,
		isSubmitHistory: !1,
		isCompute: !1
	}), e.preventDefault();
}
//#endregion
//#region src/editor/core/event/handlers/keydown/index.ts
function Nr(e, t) {
	if (t.isComposing) return;
	let n = t.getDraw();
	if (e.key === Z.Backspace) br(e, t);
	else if (e.key === Z.Delete) Sr(e, t);
	else if (e.key === Z.Enter) Tr(e, t);
	else if (e.key === Z.Left) xe && e.metaKey ? jr(e, t) : Er(e, t);
	else if (e.key === Z.Right) xe && e.metaKey ? Mr(e, t) : Dr(e, t);
	else if (e.key === Z.Up || e.key === Z.Down) Ar(e, t);
	else if (e.key === Z.Home) jr(e, t);
	else if (e.key === Z.End) Mr(e, t);
	else if (or(e) && e.key.toLocaleLowerCase() === Z.Z) {
		if (n.isReadonly() && n.getMode() !== p.FORM) return;
		n.getHistoryManager().undo(), e.preventDefault();
	} else if (or(e) && e.key.toLocaleLowerCase() === Z.Y) {
		if (n.isReadonly() && n.getMode() !== p.FORM) return;
		n.getHistoryManager().redo(), e.preventDefault();
	} else if (or(e) && e.key.toLocaleLowerCase() === Z.C) t.copy(), e.preventDefault();
	else if (or(e) && e.key.toLocaleLowerCase() === Z.X) t.cut(), e.preventDefault();
	else if (or(e) && e.key.toLocaleLowerCase() === Z.A) t.selectAll(), e.preventDefault();
	else if (or(e) && e.key.toLocaleLowerCase() === Z.S) {
		if (n.isReadonly()) return;
		let t = n.getListener();
		t.saved && t.saved(n.getValue());
		let r = n.getEventBus();
		r.isSubscribe("saved") && r.emit("saved", n.getValue()), e.preventDefault();
	} else if (e.key === Z.ESC) {
		t.clearPainterStyle();
		let r = n.getZone();
		r.isMainActive() || r.setZone(m.MAIN), e.preventDefault();
	} else e.key === Z.TAB && Or(e, t);
}
//#endregion
//#region src/editor/core/event/handlers/input.ts
function Pr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly() || n.isDisabled()) return;
	let r = n.getPosition().getCursorPosition();
	if (!e || !r) return;
	let i = t.isComposing;
	if (i && t.compositionInfo?.value === e) return;
	let a = n.getRange();
	if (!a.getIsCanInput()) return;
	let o = a.getDefaultStyle() || t.compositionInfo?.defaultStyle || null;
	Fr(t), i || n.getCursor().clearAgentDomValue();
	let { TEXT: s, HYPERLINK: c, SUBSCRIPT: l, SUPERSCRIPT: u, DATE: d, TAB: f } = H, p = e.replaceAll("\n", "​"), { startIndex: m, endIndex: h } = a.getRange(), g = n.getElementList(), _ = a.getRangeAnchorStyle(g, h);
	if (!_) return;
	let v = n.isDesignMode(), y = N(p).map((e) => {
		let t = { value: e };
		if (v || !_.title?.disabled && !_.control?.disabled) {
			let e = g[h + 1];
			(!_.type || _.type === s || _.type === c && e?.type === c || _.type === d && e?.type === d || _.type === l && e?.type === l || _.type === u && e?.type === u) && Ae.forEach((n) => {
				if (n === "groupIds" && !e?.groupIds) return;
				let r = _[n];
				r !== void 0 && (t[n] = r);
			}), (o || _.type === f) && Te.forEach((e) => {
				let n = o?.[e] || _[e];
				n !== void 0 && (t[e] = n);
			}), i && (t.underline = !0);
		}
		return t;
	});
	n.getTraceParticle().markElementListInserted(y);
	let b = n.getControl();
	if (b.getIsRangeWithinControl() && !b.getActiveControl() && (b.initControl(), !b.getActiveControl())) return;
	let x;
	if (b.getActiveControl() && b.getIsRangeWithinControl()) x = b.setValue(y), i || b.emitControlContentChange();
	else {
		let e = m + 1;
		m !== h && (n.getOptions().trace.disabled ? n.spliceElementList(g, e, h - m) : n.deleteElementList(g, e, h - m)), kn(g, y, m, { editorOptions: n.getOptions() }), n.spliceElementList(g, e, 0, y), x = m + y.length;
	}
	~x && (a.setRange(x, x), n.render({
		curIndex: x,
		isSubmitHistory: !i
	}), e && n.getAccessibility().input(e)), i && ~x && (t.compositionInfo = {
		elementList: g,
		value: p,
		startIndex: x - y.length,
		endIndex: x,
		defaultStyle: o
	});
}
function Fr(e) {
	if (!e.compositionInfo) return;
	let { elementList: t, startIndex: n, endIndex: r } = e.compositionInfo;
	t.splice(n + 1, r - n), e.getDraw().getRange().setRange(n, n), e.compositionInfo = null;
}
//#endregion
//#region src/editor/core/event/handlers/cut.ts
async function Ir(e) {
	let t = e.getDraw(), n = t.getRange(), { startIndex: r, endIndex: i } = n.getRange();
	if (!~r && !~i || t.isReadonly() || !n.getIsCanInput()) return;
	let a = t.getElementList(), o = r, s = i;
	if (r === i) {
		let e = t.getPosition().getPositionList(), n = e[r], i = n.rowNo, a = n.pageNo, c = [];
		for (let t = 0; t < e.length; t++) {
			let n = e[t];
			if (n.pageNo > a) break;
			n.pageNo === a && n.rowNo === i && c.push(t);
		}
		let l = c[0] - 1;
		o = l < 0 ? 0 : l, s = c[c.length - 1];
	}
	let c = t.getOptions();
	await Xn(a.slice(o + 1, s + 1), c);
	let l = t.getControl(), u;
	l.getActiveControl() && l.getIsRangeWithinControl() ? (u = l.cut(), l.emitControlContentChange()) : (t.deleteElementList(a, o + 1, s - o), u = o), n.setRange(u, u), t.render({ curIndex: u });
}
//#endregion
//#region src/editor/core/event/handlers/copy.ts
async function Lr(e, t) {
	let n = e.getDraw(), { copy: r } = n.getOverride();
	if (r && r()?.preventDefault !== !1) return;
	let i = n.getRange(), a = null;
	if (i.getRange().isCrossRowCol) {
		let e = i.getRangeTableElement();
		if (!e) return;
		let t = n.getTableParticle().getRangeRowCol();
		if (!t) return;
		let r = {
			type: H.TABLE,
			value: "",
			colgroup: [],
			trList: []
		}, o = t[0], s = o[0].colIndex, c = o[o.length - 1], l = c.colIndex + c.colspan - 1;
		for (let t = s; t <= l; t++) r.colgroup.push(e.colgroup[t]);
		for (let n = 0; n < t.length; n++) {
			let i = t[n], a = e.trList[i[0].rowIndex], o = {
				tdList: [],
				height: a.height,
				minHeight: a.minHeight
			};
			for (let e = 0; e < i.length; e++) o.tdList.push(i[e]);
			r.trList.push(o);
		}
		a = X([r]);
	} else a = i.getIsCollapsed() ? i.getRangeRowElementList() : i.getSelectionElementList();
	t?.isPlainText && a?.length && (a = [{ value: In(gn(a)) }]), a?.length && await Xn(a, n.getOptions());
}
//#endregion
//#region src/editor/core/event/handlers/drop.ts
function Rr(e, t) {
	let { drop: n } = t.getDraw().getOverride();
	if (n && n(e)?.preventDefault !== !1) return;
	e.preventDefault();
	let r = e.dataTransfer?.getData("text");
	if (r) t.input(r);
	else {
		let n = e.dataTransfer?.files;
		if (!n) return;
		for (let e = 0; e < n.length; e++) {
			let r = n[e];
			r.type.startsWith("image") && er(t, r);
		}
	}
}
//#endregion
//#region src/editor/core/event/handlers/click.ts
function zr(e) {
	if (!Intl.Segmenter) return null;
	let t = e.getDraw(), n = t.getPosition().getCursorPosition();
	if (!n) return null;
	let r = t.getRange().getRangeParagraphInfo();
	if (!r) return null;
	let i = r?.elementList?.map((e) => !e.type || e.type !== H.CONTROL && Be.includes(e.type) ? e.value : "​").join("") || "";
	if (!i) return null;
	let a = n.isFirstLetter || t.getCursor().getHitLineStartIndex() ? n.index + 1 : n.index, o = r.startIndex, s = new Intl.Segmenter(void 0, { granularity: "word" }).segment(i), c = -1, l = -1;
	for (let { segment: e, index: t, isWordLike: n } of s) {
		let r = t + o;
		if (n && a >= r && a < r + e.length) {
			c = r - 1, l = c + e.length;
			break;
		}
	}
	return ~c && ~l ? {
		startIndex: c,
		endIndex: l
	} : null;
}
function Br(e) {
	let t = e.getDraw(), n = t.getPosition().getCursorPosition();
	if (!n) return null;
	let { value: r, index: i } = n, a = t.getLetterReg(), o = 0, s = 0, c = b.test(r);
	if (c || a.test(r)) {
		let e = t.getElementList(), n = i - 1;
		for (; n > 0;) {
			let t = e[n].value;
			if (c && b.test(t) || !c && a.test(t)) o++, n--;
			else break;
		}
		let r = i + 1;
		for (; r < e.length;) {
			let t = e[r].value;
			if (c && b.test(t) || !c && a.test(t)) s++, r++;
			else break;
		}
	}
	let l = i - o - 1;
	return l < 0 ? null : {
		startIndex: l,
		endIndex: i + s
	};
}
function Vr(e, t) {
	let n = e.getDraw(), r = n.getPosition(), i = r.getPositionByXY({
		x: t.offsetX,
		y: t.offsetY
	});
	if (i.isImage && i.isDirectHit) {
		let e = n.getElementList(), r = n.getEventBus(), a = e[i.index];
		if (r.isSubscribe("imageDblclick") && r.emit("imageDblclick", {
			evt: t,
			element: a
		}), a.imgPreviewDisabled) return;
		n.getPreviewer().render();
		return;
	}
	if (n.getIsPagingMode() && !~i.index && i.zone) {
		n.getZone().setZone(i.zone), n.clearSideEffect(), r.setPositionContext({ isTable: !1 });
		return;
	}
	if ((i.isCheckbox || i.isRadio) && i.isDirectHit) return;
	let a = n.getRange(), o = zr(e) || Br(e);
	o && (a.setRange(o.startIndex, o.endIndex), n.render({
		isSubmitHistory: !1,
		isSetCursor: !1,
		isCompute: !1
	}), a.setRangeStyle());
}
function Hr(e) {
	let t = e.getDraw(), n = t.getControl();
	if (n.getActiveControl() && n.selectValue()) return;
	let r = t.getPosition().getCursorPosition();
	if (!r) return;
	let { index: i } = r, a = t.getElementList(), o = 0, s = 0, c = i - 1;
	for (; c > 0;) {
		let e = a[c], t = a[c - 1];
		if (e.value === "​" && !e.listWrap || e.listId !== t?.listId || e.titleId !== t?.titleId) break;
		o++, c--;
	}
	let l = i + 1;
	for (; l < a.length;) {
		let e = a[l], t = a[l + 1];
		if (e.value === "​" && !e.listWrap || e.listId !== t?.listId || e.titleId !== t?.titleId) break;
		s++, l++;
	}
	let u = t.getRange(), d = i - o - 1;
	if (a[d]?.value !== "​" && --d, d < 0) return;
	let f = i + s + 1;
	(a[f]?.value === "​" || f > a.length - 1) && --f, u.setRange(d, f), t.render({
		isSubmitHistory: !1,
		isSetCursor: !1,
		isCompute: !1
	});
}
var Ur = {
	dblclick: Vr,
	threeClick: Hr
};
//#endregion
//#region src/editor/core/event/handlers/composition.ts
function Wr(e) {
	e.isComposing = !0;
}
function Gr(e, t) {
	e.isComposing = !1;
	let n = e.getDraw();
	if (t.data) we ? setTimeout(() => {
		e.compositionInfo && Pr(t.data, e);
	}, 1) : e.compositionInfo && Pr(t.data, e);
	else {
		Fr(e);
		let { endIndex: t } = n.getRange().getRange();
		n.render({
			curIndex: t,
			isSubmitHistory: !1
		});
	}
	n.getCursor().clearAgentDomValue();
}
var Kr = {
	compositionstart: Wr,
	compositionend: Gr
};
//#endregion
//#region src/editor/core/event/handlers/drag.ts
function qr(e, t) {
	let n = t.getDraw();
	if (n.isReadonly()) return;
	e.preventDefault();
	let i = n.getPageContainer();
	if (!j(e.target, (e) => e === i, !0)) return;
	let a = e.target.dataset.index;
	a && n.setPageNo(Number(a));
	let o = n.getPosition(), s = o.adjustPositionContext({
		x: e.offsetX,
		y: e.offsetY
	});
	if (!s) return;
	let { isTable: c, tdValueIndex: l, index: u } = s, d = o.getPositionList(), f = c ? l : u;
	~u && (n.getRange().setRange(f, f), o.setCursorPosition(d[f]));
	let p = n.getCursor(), { cursor: { dragColor: m, dragWidth: h, dragFloatImageDisabled: g } } = n.getOptions();
	if (g) {
		let e = t.cacheElementList?.[t.cacheRange.startIndex];
		if (e?.type === H.IMAGE && (e.imgDisplay === r.FLOAT_TOP || e.imgDisplay === r.FLOAT_BOTTOM || e.imgDisplay === r.SURROUND)) return;
	}
	p.drawCursor({
		width: h,
		color: m,
		isBlink: !1,
		isFocus: !1
	});
}
var Jr = { dragover: qr }, Yr = class {
	isAllowSelection;
	isComposing;
	compositionInfo;
	isAllowDrag;
	isAllowDrop;
	cacheRange;
	cacheElementList;
	cachePositionList;
	cachePositionContext;
	mouseDownStartPosition;
	draw;
	pageContainer;
	pageList;
	range;
	position;
	constructor(e) {
		this.draw = e, this.pageContainer = e.getPageContainer(), this.pageList = e.getPageList(), this.range = this.draw.getRange(), this.position = this.draw.getPosition(), this.isAllowSelection = !1, this.isComposing = !1, this.compositionInfo = null, this.isAllowDrag = !1, this.isAllowDrop = !1, this.cacheRange = null, this.cacheElementList = null, this.cachePositionList = null, this.cachePositionContext = null, this.mouseDownStartPosition = null;
	}
	getDraw() {
		return this.draw;
	}
	register() {
		this.pageContainer.addEventListener("click", this.click.bind(this)), this.pageContainer.addEventListener("mousedown", this.mousedown.bind(this)), this.pageContainer.addEventListener("mouseup", this.mouseup.bind(this)), this.pageContainer.addEventListener("mouseleave", this.mouseleave.bind(this)), this.pageContainer.addEventListener("mousemove", this.mousemove.bind(this)), this.pageContainer.addEventListener("dblclick", this.dblclick.bind(this)), this.pageContainer.addEventListener("dragover", this.dragover.bind(this)), this.pageContainer.addEventListener("drop", this.drop.bind(this)), P(this.pageContainer, this.threeClick.bind(this));
	}
	setIsAllowSelection(e) {
		this.isAllowSelection = e, e || this.applyPainterStyle();
	}
	setIsAllowDrag(e) {
		this.isAllowDrag = e, this.isAllowDrop = e;
	}
	clearPainterStyle() {
		this.pageList.forEach((e) => {
			e.style.cursor = "text";
		}), this.draw.setPainterStyle(null);
	}
	applyPainterStyle() {
		let e = this.draw.getPainterStyle();
		if (!e || this.draw.isReadonly() || this.draw.isDisabled()) return;
		let t = this.range.getSelection();
		if (!t) {
			let e = zr(this);
			e && (t = this.draw.getElementList().slice(e.startIndex + 1, e.endIndex + 1));
		}
		if (!t) return;
		let n = ke, r = Object.keys(e).filter((e) => !n.includes(e));
		t.forEach((t) => {
			r.forEach((n) => {
				let r = n;
				Reflect.set(t, r, e[r]);
			});
		});
		let i = this.range.getRangeParagraphElementList();
		if (i && i.length === t.length && i.every((e) => t.includes(e))) {
			let t = e.level ? M() : null;
			for (let n = 0; n < i.length; n++) {
				let r = i[n];
				r.rowFlex = e.rowFlex, r.rowMargin = e.rowMargin, e.level && t ? (r.level = e.level, r.title = e.title, r.titleId = t) : (delete r.level, delete r.title, delete r.titleId);
			}
		}
		this.draw.render({ isSetCursor: !1 });
		let a = this.draw.getPainterOptions();
		(!a || !a.isDblclick) && this.clearPainterStyle();
	}
	selectAll() {
		if (this.position.getPositionContext().isTable) this.draw.getTableOperate().tableSelectAll();
		else {
			let e = this.position.getPositionList();
			this.range.setRange(0, e.length - 1), this.draw.render({
				isSubmitHistory: !1,
				isSetCursor: !1,
				isCompute: !1
			});
		}
	}
	mousemove(e) {
		vr(e, this);
	}
	mousedown(e) {
		fr(e, this);
	}
	click() {
		Se && !this.draw.isReadonly() && this.draw.getCursor().getAgentDom().focus();
	}
	mouseup(e) {
		gr(e, this);
	}
	mouseleave(e) {
		_r(e, this);
	}
	keydown(e) {
		Nr(e, this);
	}
	dblclick(e) {
		Ur.dblclick(this, e);
	}
	threeClick() {
		Ur.threeClick(this);
	}
	input(e) {
		Pr(e, this);
	}
	async cut() {
		await Ir(this);
	}
	async copy(e) {
		await Lr(this, e);
	}
	compositionstart() {
		Kr.compositionstart(this);
	}
	compositionend(e) {
		Kr.compositionend(this, e);
	}
	drop(e) {
		Rr(e, this);
	}
	dragover(e) {
		Jr.dragover(e, this);
	}
}, Xr = { PAGE_SCALE: "pageScale" }, Zr = class {
	draw;
	options;
	cursor;
	canvasEvent;
	range;
	previewer;
	tableTool;
	hyperlinkParticle;
	hintParticle;
	control;
	magnifier;
	dateParticle;
	imageParticle;
	dprMediaQueryList;
	constructor(e, t) {
		this.draw = e, this.options = e.getOptions(), this.canvasEvent = t, this.cursor = null, this.range = e.getRange(), this.previewer = e.getPreviewer(), this.tableTool = e.getTableTool(), this.hyperlinkParticle = e.getHyperlinkParticle(), this.hintParticle = e.getHintParticle(), this.dateParticle = e.getDateParticle(), this.imageParticle = e.getImageParticle(), this.control = e.getControl(), this.magnifier = e.getMagnifier(), this.dprMediaQueryList = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`);
	}
	register() {
		this.cursor = this.draw.getCursor(), this.addEvent();
	}
	addEvent() {
		window.addEventListener("blur", this.clearSideEffect), document.addEventListener("mousedown", this.clearSideEffect), document.addEventListener("mouseup", this.setCanvasEventAbility), document.addEventListener("wheel", this.setPageScale, { passive: !1 }), document.addEventListener("visibilitychange", this._handleVisibilityChange), this.dprMediaQueryList.addEventListener("change", this._handleDprChange);
	}
	removeEvent() {
		window.removeEventListener("blur", this.clearSideEffect), document.removeEventListener("mousedown", this.clearSideEffect), document.removeEventListener("mouseup", this.setCanvasEventAbility), document.removeEventListener("wheel", this.setPageScale), document.removeEventListener("visibilitychange", this._handleVisibilityChange), this.dprMediaQueryList.removeEventListener("change", this._handleDprChange);
	}
	clearSideEffect = (e) => {
		if (!this.cursor) return;
		let t = e?.composedPath()[0] || e.target, n = this.draw.getPageList();
		if (!j(t, (e) => n.includes(e), !0)) {
			if (j(t, (e) => !!e && e.nodeType === 1 && !!e.getAttribute("editor-component"), !0)) {
				this.watchCursorActive();
				return;
			}
			this.cursor.recoveryCursor(), this.range.recoveryRangeStyle(), this.previewer.clearResizer(), this.tableTool.dispose(), this.hyperlinkParticle.clearHyperlinkPopup(), this.hintParticle.clearHintPopup(), this.control.destroyControl(), this.dateParticle.clearDatePicker(), this.imageParticle.destroyFloatImage(), this.magnifier.hide();
		}
	};
	setCanvasEventAbility = () => {
		this.canvasEvent.setIsAllowDrag(!1), this.canvasEvent.setIsAllowSelection(!1);
	};
	watchCursorActive() {
		this.range.getIsCollapsed() && setTimeout(() => {
			this.cursor?.getAgentIsActive() || this.cursor?.drawCursor({
				isFocus: !1,
				isBlink: !1
			});
		});
	}
	setPageScale = (e) => {
		if (this.options.shortcutDisableKeys.includes(Xr.PAGE_SCALE) || !e.ctrlKey) return;
		e.preventDefault();
		let { scale: t } = this.options;
		if (e.deltaY < 0) {
			let e = t * 10 + 1;
			e <= 30 && this.draw.setPageScale(e / 10);
		} else {
			let e = t * 10 - 1;
			e >= 5 && this.draw.setPageScale(e / 10);
		}
	};
	_handleVisibilityChange = () => {
		if (document.visibilityState === "visible") {
			let e = this.range.getRange(), t = !!~e.startIndex && !!~e.endIndex && e.startIndex === e.endIndex;
			this.range.replaceRange(e), this.draw.render({
				isSetCursor: t,
				isCompute: !1,
				isSubmitHistory: !1,
				curIndex: e.startIndex
			});
		}
	};
	_handleDprChange = () => {
		this.draw.setPageDevicePixel();
	};
}, Qr = class {
	undoStack = [];
	redoStack = [];
	maxRecordCount;
	constructor(e) {
		this.maxRecordCount = e.getOptions().historyMaxRecordCount + 1;
	}
	undo() {
		if (this.undoStack.length > 1) {
			let e = this.undoStack.pop();
			this.redoStack.push(e), this.undoStack.length && this.undoStack[this.undoStack.length - 1]();
		}
	}
	redo() {
		if (this.redoStack.length) {
			let e = this.redoStack.pop();
			this.undoStack.push(e), e();
		}
	}
	execute(e) {
		for (this.undoStack.push(e), this.redoStack.length && (this.redoStack = []); this.undoStack.length > this.maxRecordCount;) this.undoStack.shift();
	}
	isCanUndo() {
		return this.undoStack.length > 1;
	}
	isCanRedo() {
		return !!this.redoStack.length;
	}
	isStackEmpty() {
		return !this.undoStack.length && !this.redoStack.length;
	}
	recovery() {
		this.undoStack = [], this.redoStack = [];
	}
	popUndo() {
		return this.undoStack.pop();
	}
}, $r = class {
	cursorPosition;
	positionContext;
	positionList;
	tablePagingPositionList;
	tablePagingPositionMap;
	floatPositionList;
	draw;
	eventBus;
	options;
	constructor(e) {
		this.positionList = [], this.tablePagingPositionList = [], this.tablePagingPositionMap = /* @__PURE__ */ new Map(), this.floatPositionList = [], this.cursorPosition = null, this.positionContext = {
			isTable: !1,
			isControl: !1
		}, this.draw = e, this.eventBus = e.getEventBus(), this.options = e.getOptions();
	}
	getFloatPositionList() {
		return this.floatPositionList;
	}
	getTablePagingPositionList() {
		return this.tablePagingPositionList;
	}
	getTableFragmentPosition(e, t, n) {
		let r = this.tablePagingPositionMap.get(t);
		if (!r?.length) return null;
		let i = r.filter((t) => t.index === e);
		if (i.length <= 1) return i[0] || null;
		if (n) {
			let { coordinate: { leftTop: e, rightBottom: t } } = n, r = i.find((n) => {
				let { leftTop: r, rightTop: i, leftBottom: a } = n.coordinate;
				return e[0] >= r[0] && t[0] <= i[0] && e[1] >= r[1] && t[1] <= a[1];
			});
			if (r) return r;
		}
		return i[0];
	}
	getTablePositionList(e) {
		return this.getTableTdByContext(e, this.positionContext)?.positionList || [];
	}
	getTableTdByContext(e, t) {
		let n = t.tablePath?.length ? t.tablePath : this._getTablePathByContext(t), r = e, i = null;
		for (let e = 0; e < n.length; e++) {
			let { index: t, trIndex: a, tdIndex: o } = n[e];
			if (i = r[t]?.trList?.[a]?.tdList[o] || null, !i) return null;
			r = i.value;
		}
		return i;
	}
	buildTablePositionContext(e, t, n, r) {
		let i = t.trList[n], a = i.tdList[r], o = e.tablePath?.length ? e.tablePath.map((e, o, s) => o === s.length - 1 ? {
			...e,
			trIndex: n,
			tdIndex: r,
			tdId: a.id,
			trId: i.id,
			tableId: t.id
		} : e) : void 0;
		return {
			...e,
			isTable: !0,
			trIndex: n,
			tdIndex: r,
			tdId: a.id,
			trId: i.id,
			tableId: t.id,
			tablePath: o
		};
	}
	getTableElementByContext(e, t) {
		let n = t.tablePath?.length ? t.tablePath : this._getTablePathByContext(t), r = e, i = null;
		for (let e = 0; e < n.length; e++) {
			let { index: t, trIndex: a, tdIndex: o } = n[e];
			if (i = r[t] || null, !i) return null;
			if (e === n.length - 1) break;
			let s = i.trList?.[a]?.tdList[o];
			if (!s) return null;
			r = s.value;
		}
		return i;
	}
	getTableElementPositionByContext(e, t, n) {
		let r = n.tablePath?.length ? n.tablePath : this._getTablePathByContext(n), i = e, a = t, o = null;
		for (let e = 0; e < r.length; e++) {
			let { index: t, trIndex: n, tdIndex: s } = r[e];
			o = a[t] || null;
			let c = i[t];
			if (!o || !c) return null;
			if (e === r.length - 1) break;
			let l = c.trList?.[n]?.tdList[s];
			if (!l) return null;
			i = l.value, a = l.positionList || [];
		}
		if (o?.tableFragment) {
			let t = this.getTableTdByContext(e, n), r = this.getCursorPosition(), i = !!t && !!r && !!t.positionList?.includes(r), a = i ? r.pageNo : t?.positionList?.[0]?.pageNo;
			if (a !== void 0) {
				let e = this.getTableFragmentPosition(o.index, a, i ? r : t?.positionList?.[0]);
				if (e) return e;
			}
		}
		return o;
	}
	_getTablePathByContext(e) {
		let { isTable: t, index: n, trIndex: r, tdIndex: i, tdId: a, trId: o, tableId: s } = e;
		return !t || n === void 0 || r === void 0 || i === void 0 ? [] : [{
			index: n,
			trIndex: r,
			tdIndex: i,
			tdId: a,
			trId: o,
			tableId: s
		}];
	}
	getPositionList() {
		return this.positionContext.isTable ? this.getTablePositionList(this.draw.getOriginalElementList()) : this.getOriginalPositionList();
	}
	getMainPositionList() {
		return this.positionContext.isTable ? this.getTablePositionList(this.draw.getOriginalMainElementList()) : this.positionList;
	}
	getOriginalPositionList() {
		let e = this.draw.getZone(), t = this.draw.getPageDirection(this.draw.getPageNo());
		return e.isHeaderActive() ? this.draw.getHeader().getPositionList(t) : e.isFooterActive() ? this.draw.getFooter().getPositionList(t) : this.positionList;
	}
	getOriginalMainPositionList() {
		return this.positionList;
	}
	getSelectionPositionList() {
		let { startIndex: e, endIndex: t } = this.draw.getRange().getRange();
		return e === t ? null : this.getPositionList().slice(e + 1, t + 1);
	}
	setPositionList(e) {
		this.positionList = e;
	}
	setFloatPositionList(e) {
		this.floatPositionList = e;
	}
	getFloatPositionByElement(e) {
		return this.floatPositionList.find((t) => t.element === e) || null;
	}
	getFloatPositionCoordinate(e) {
		let { scale: t } = this.options, n = e.element.imgFloatPosition, r = n.x * t, i = n.y * t, { index: a, isTable: o, zone: s } = e;
		if (o && a !== void 0) {
			let t, n = this.draw.getPageDirection(e.pageNo ?? this.draw.getPageNo());
			t = s === m.HEADER ? this.draw.getHeader().getPositionList(n) : s === m.FOOTER ? this.draw.getFooter().getPositionList(n) : this.positionList;
			let o = t[a];
			if (o?.tableFragment && (o = this.getTableFragmentPosition(a, e.pageNo, e.position) || o), o) {
				let { coordinate: { leftTop: [e, t] } } = o;
				r += e, i += t;
			}
		}
		return {
			x: r,
			y: i
		};
	}
	computePageRowPosition(e) {
		let { positionList: t, rowList: n, pageNo: i, startX: a, startY: o, startRowIndex: s, startIndex: c, innerWidth: l, zone: d, tablePosition: f } = e, { scale: p, table: { tdPadding: m } } = this.options, h = a, g = o, _ = c, v = this.draw.getTraceParticle(), y = this.draw.getColumnLayout(), b;
		for (let c = 0; c < n.length; c++) {
			let x = n[c];
			b !== void 0 && x.columnIndex !== void 0 && x.columnIndex > 0 && x.columnIndex !== b && (g = o), b = x.columnIndex;
			let S = y && x.columnIndex !== void 0 && x.columnIndex >= 0, C = S && y && y.offsets[x.columnIndex] || 0, w = S && y ? y.width : l;
			if (h += C, !x.isSurround) {
				let e = x.width + (x.offsetX || 0);
				x.rowFlex === u.CENTER ? h += (w - e) / 2 : x.rowFlex === u.RIGHT && (h += w - e);
			}
			h += x.offsetX || 0, g += x.offsetY || 0;
			let T = h, E = g;
			for (let n = 0; n < x.elementList.length; n++) {
				let a = x.elementList[n];
				x.tableFragment && (_ = x.startIndex + n);
				let o = a.metrics, l = !a.hide && !v.isTraceHidden(a) && (a.imgDisplay !== r.INLINE && a.type === H.IMAGE || a.type === H.LATEX) ? x.ascent - o.height : x.ascent;
				a.left && (h += a.left), a.translateX && (h += a.translateX * p);
				let u = {
					pageNo: i,
					index: _,
					value: a.value,
					rowIndex: s + c,
					rowNo: e.isTable ? s + c : c,
					metrics: o,
					left: a.left || 0,
					ascent: l,
					lineHeight: x.height,
					isFirstLetter: n === 0,
					isLastLetter: n === x.elementList.length - 1,
					columnIndex: x.columnIndex,
					coordinate: {
						leftTop: [h, g],
						leftBottom: [h, g + x.height],
						rightTop: [h + o.width, g],
						rightBottom: [h + o.width, g + x.height]
					}
				};
				if (a.imgDisplay === r.SURROUND || a.imgDisplay === r.FLOAT_TOP || a.imgDisplay === r.FLOAT_BOTTOM) {
					let n = t[t.length - 1];
					if (n && (u.metrics = n.metrics, u.coordinate = n.coordinate), !a.imgFloatPosition) {
						let e = f?.coordinate.leftTop;
						a.imgFloatPosition = {
							x: e ? h - e[0] : h,
							y: e ? g - e[1] : g,
							pageNo: i
						};
					}
					this.floatPositionList.push({
						pageNo: i,
						element: a,
						position: u,
						isTable: e.isTable,
						index: e.index,
						tdIndex: e.tdIndex,
						trIndex: e.trIndex,
						tdValueIndex: _,
						zone: d
					});
				}
				let y = x.tableFragment;
				if (y) {
					u.tableFragment = y, x.fragmentPosition = u, this.tablePagingPositionList.push(u);
					let e = this.tablePagingPositionMap.get(i) || [];
					e.push(u), this.tablePagingPositionMap.set(i, e), y.startTrIndex === 0 && !y.startSplitTrOffset && t.push(u);
				} else t.push(u);
				if (_++, h += o.width, a.type === H.TABLE && !a.hide && !v.isTraceHidden(a)) {
					let e = m[1] + m[3], t = y ? this.draw.getTableParticle().getFragmentTdList(a, y) : a.trList.flatMap((e) => e.tdList);
					for (let n of t) {
						let t = !1, r = !1, o = 0, s = n.height;
						if (y) {
							if ([o, s] = this.draw.getTableParticle().getTdWindowInFragment(n, a, y), s <= o) continue;
							t = o > 0 || s < n.height, r = o > 0;
						}
						let c = n.rowList, l = 0, f = 0;
						if (t) {
							let e = this.draw.getTableParticle().getTdVisibleRowListByWindow(n, o, s);
							c = e.rowList, l = e.startIndex, f = e.startRowIndex;
						}
						r || (n.positionList = []);
						let v = n.positionList, b = y ? this.draw.getTableParticle().getTdWindowOffsetY(o, y) : 0, x = this.computePageRowPosition({
							positionList: v,
							rowList: c,
							pageNo: i,
							startRowIndex: f,
							startIndex: l,
							startX: (n.x + m[3]) * p + T + (a.translateX || 0) * p,
							startY: (n.y + m[0]) * p + E + b,
							innerWidth: (n.width - e) * p,
							isTable: !0,
							index: _ - 1,
							tdIndex: n.tdIndex,
							trIndex: n.rowIndex,
							zone: d,
							tablePosition: u
						});
						t || this._offsetTdPositionByVerticalAlign(n, v), h = x.x, g = x.y;
					}
					if (y?.repeatTrIndexes?.length) {
						x.repeatTdPositionList = [];
						let t = 0;
						for (let n of y.repeatTrIndexes) {
							let r = a.trList[n];
							for (let o = 0; o < r.tdList.length; o++) {
								let s = r.tdList[o], c = [];
								this.computePageRowPosition({
									positionList: c,
									rowList: s.rowList,
									pageNo: i,
									startRowIndex: 0,
									startIndex: 0,
									startX: (s.x + m[3]) * p + T + (a.translateX || 0) * p,
									startY: (t + m[0]) * p + E,
									innerWidth: (s.width - e) * p,
									isTable: !0,
									index: _ - 1,
									tdIndex: o,
									trIndex: n,
									zone: d,
									tablePosition: u
								}), this._offsetTdPositionByVerticalAlign(s, c), x.repeatTdPositionList.push({
									td: s,
									positionList: c
								});
							}
							t += r.height;
						}
					}
					h = T, g = E;
				}
			}
			h = a, g += x.height;
		}
		return {
			x: h,
			y: g,
			index: _
		};
	}
	_offsetTdPositionByVerticalAlign(e, t) {
		if (e.verticalAlign !== Y.MIDDLE && e.verticalAlign !== Y.BOTTOM) return;
		let { scale: n, table: { tdPadding: r } } = this.options, i = r[0] + r[2], a = e.rowList.reduce((e, t) => e + t.height, 0), o = (e.height - i) * n - a, s = e.verticalAlign === Y.MIDDLE ? o / 2 : o;
		Math.floor(s) > 0 && t.forEach((e) => {
			let { coordinate: { leftTop: t, leftBottom: n, rightBottom: r, rightTop: i } } = e;
			t[1] += s, n[1] += s, r[1] += s, i[1] += s;
		});
	}
	computePositionList() {
		this.positionList = [], this.tablePagingPositionList = [], this.tablePagingPositionMap.clear();
		let e = this.draw.getPageRowList(), t = this.draw.getHeader(), n = 0;
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			if (!i?.length) continue;
			let a = i[0].startIndex, { margins: o, innerWidth: s } = this.draw.getPageSize(r), c = o[3], l = o[0] + t.getExtraHeight(r);
			this.computePageRowPosition({
				positionList: this.positionList,
				rowList: i,
				pageNo: r,
				startRowIndex: n,
				startIndex: a,
				startX: c,
				startY: l,
				innerWidth: s
			}), n += i.length;
		}
	}
	computeRowPosition(e) {
		let { row: t, innerWidth: n } = e, r = [];
		return this.computePageRowPosition({
			positionList: r,
			innerWidth: n,
			rowList: [k(t)],
			pageNo: 0,
			startX: 0,
			startY: 0,
			startIndex: 0,
			startRowIndex: 0
		}), r;
	}
	setCursorPosition(e) {
		this.cursorPosition = e;
	}
	getCursorPosition() {
		return this.cursorPosition;
	}
	getPositionContext() {
		return this.positionContext;
	}
	setPositionContext(e) {
		this.eventBus.emit("positionContextChange", {
			value: e,
			oldValue: this.positionContext
		}), this.positionContext = e;
	}
	_getColumnIndexByX(e) {
		let t = this.draw.getColumnLayout();
		if (!t) return;
		let n = e - this.draw.getMargins()[3];
		for (let e = 0; e < t.count; e++) {
			let r = t.offsets[e], i = e < t.count - 1 ? t.offsets[e + 1] : r + t.width;
			if (n >= r && n < i) return e;
		}
		return t.count - 1;
	}
	_getTableChildPositionByXY(e) {
		let { x: t, y: n, pageNo: r, element: i, index: a, tablePosition: o } = e, { scale: s } = this.options, c = o.tableFragment, l = c ? this.draw.getTableParticle().getFragmentTdList(i, c) : i.trList.flatMap((e) => e.tdList);
		for (let e of l) {
			let l = e.rowIndex, u = e.tdIndex, d = i.trList[l];
			if (c) {
				let [t, r] = this.draw.getTableParticle().getTdWindowInFragment(e, i, c);
				if (r <= t) continue;
				let a = o.coordinate.leftTop[1] + e.y * s + this.draw.getTableParticle().getTdWindowOffsetY(t, c), l = a + (r - t) * s;
				if (n < a || n > l) continue;
			}
			let f = this.getPositionByXY({
				x: t,
				y: n,
				td: e,
				pageNo: r,
				tablePosition: o,
				isTable: !0,
				elementList: e.value,
				positionList: e.positionList
			});
			if (~f.index) {
				let { index: t, isTable: n, hitLineStartIndex: r, tablePath: o = [] } = f, s = {
					index: a,
					trIndex: l,
					tdIndex: u,
					tdId: e.id,
					trId: d.id,
					tableId: i.id
				};
				if (n) return {
					...f,
					index: a,
					tablePath: [s, ...o],
					hitLineStartIndex: r
				};
				let c = e.value[t];
				return {
					index: a,
					isCheckbox: f.isCheckbox || c.type === H.CHECKBOX || c.controlComponent === K.CHECKBOX,
					isRadio: c.type === H.RADIO || c.controlComponent === K.RADIO,
					isControl: !!c.controlId,
					isImage: f.isImage,
					isDirectHit: f.isDirectHit,
					isTable: !0,
					tdIndex: u,
					trIndex: l,
					tdValueIndex: t,
					tdId: e.id,
					trId: d.id,
					tableId: i.id,
					tablePath: [s],
					hitLineStartIndex: r
				};
			}
		}
		return null;
	}
	getPositionByXY(e) {
		let { x: t, y: n, isTable: i } = e, { elementList: a, positionList: o } = e;
		a ||= this.draw.getOriginalElementList(), o ||= this.getOriginalPositionList();
		let s = this.draw.getZone(), c = e.pageNo ?? this.draw.getPageNo(), l = s.isMainActive(), u = c;
		if (!i) {
			let t = this.getFloatPositionByXY({
				...e,
				imgDisplays: [r.FLOAT_TOP, r.SURROUND]
			});
			if (t) return t;
		}
		for (let e = 0; e < o.length; e++) {
			let { index: r, pageNo: i, left: s, isFirstLetter: d, coordinate: { leftTop: f, rightTop: p, leftBottom: m } } = o[e];
			if (l) {
				if (u !== i) continue;
				if (i > u) break;
			}
			if (f[0] - s <= t && p[0] >= t && f[1] <= n && m[1] >= n) {
				let i = e, s = a[e];
				if (s.type === H.TABLE) {
					let i = this._getTableChildPositionByXY({
						x: t,
						y: n,
						pageNo: c,
						element: s,
						index: r,
						tablePosition: o[e]
					});
					if (i) return i;
				}
				if (s.type === H.IMAGE || s.type === H.LATEX) return {
					index: i,
					isDirectHit: !0,
					isImage: !0
				};
				if (s.type === H.CHECKBOX || s.controlComponent === K.CHECKBOX) return {
					index: i,
					isDirectHit: !0,
					isCheckbox: !0
				};
				if (s.type === H.LABEL) return {
					index: i,
					isDirectHit: !0,
					isLabel: !0
				};
				if (s.type === H.TAB && s.listStyle === _t.CHECKBOX) {
					let e = i - 1;
					for (; e > 0;) {
						let t = a[e];
						if (t.value === "​" && t.listStyle === _t.CHECKBOX) break;
						e--;
					}
					return {
						index: e,
						isDirectHit: !0,
						isCheckbox: !0
					};
				}
				if (s.type === H.RADIO || s.controlComponent === K.RADIO) return {
					index: i,
					isDirectHit: !0,
					isRadio: !0
				};
				let l;
				if (a[r].value !== "​") {
					let n = p[0] - f[0];
					t < f[0] + n / 2 && (i = e - 1, d && (l = e));
				}
				return {
					isDirectHit: !0,
					hitLineStartIndex: l,
					index: i,
					isControl: !!s.controlId
				};
			}
		}
		if (!i && l) {
			let e = this.tablePagingPositionMap.get(c) || [];
			for (let r of e) {
				let { index: e, coordinate: { leftTop: i, rightTop: o, leftBottom: s } } = r;
				if (i[0] <= t && o[0] >= t && i[1] <= n && s[1] >= n) {
					let i = a[e];
					if (i?.type === H.TABLE) {
						let a = this._getTableChildPositionByXY({
							x: t,
							y: n,
							pageNo: c,
							element: i,
							index: e,
							tablePosition: r
						});
						if (a) return a;
					}
				}
			}
		}
		if (!i) {
			let t = this.getFloatPositionByXY({
				...e,
				imgDisplays: [r.FLOAT_BOTTOM]
			});
			if (t) return t;
		}
		let d = !1, f = -1, p;
		if (i) {
			let { scale: r } = this.options, { td: i, tablePosition: a } = e;
			if (i && a) {
				let { leftTop: e } = a.coordinate, o = a.tableFragment, s = 0;
				if (o) {
					let e = o.startSplitTrOffset && i.trIndex > o.startTrIndex ? o.startSplitTrOffset : 0;
					s = (o.repeatHeight - o.skipHeight - e) * r;
				}
				let c = i.x * r + e[0], l = i.y * r + e[1] + s, u = i.width * r, d = i.height * r;
				if (!(c < t && t < c + u && l < n && n < l + d)) return { index: f };
			}
		}
		let h = l ? o.filter((e) => e.isLastLetter && e.pageNo === u) : o.filter((e) => e.isLastLetter), g = this._getColumnIndexByX(t), _ = g === void 0 ? h : h.filter((e) => e.columnIndex === void 0 || g === e.columnIndex);
		for (let e = 0; e < _.length; e++) {
			let { index: r, rowNo: i, coordinate: { leftTop: s, leftBottom: c } } = _[e];
			if (n > s[1] && n <= c[1]) {
				let e = l ? o.findIndex((e) => e.pageNo === u && e.rowNo === i) : o.findIndex((e) => e.rowNo === i), n = a[e], c = o[e];
				if (t < (n.listStyle === _t.CHECKBOX ? this.draw.getMargins()[3] : c.coordinate.leftTop[0])) ~e ? c.value === "​" ? f = e : (f = e - 1, p = e) : f = r;
				else {
					if (n.listStyle === _t.CHECKBOX && t < s[0]) return {
						index: e,
						isDirectHit: !0,
						isCheckbox: !0
					};
					f = r;
				}
				d = !0;
				break;
			}
		}
		if (!d) {
			if (this.draw.getIsPagingMode()) {
				let e = this.draw.getHeader(), t = e.isDisabled(c), r = t ? 0 : e.getHeaderTop(c) + e.getHeight(c), i = this.draw.getFooter(), a = i.isDisabled(c), { height: o } = this.draw.getPageSize(c), s = a ? o : o - (i.getFooterBottom(c) + i.getHeight(c));
				if (l) {
					if (!t && n < r) return {
						index: -1,
						zone: m.HEADER
					};
					if (!a && n > s) return {
						index: -1,
						zone: m.FOOTER
					};
				} else if (n <= s && n >= r) return {
					index: -1,
					zone: m.MAIN
				};
			}
			let e = this.draw.getMargins();
			if (n <= e[0]) for (let n = 0; n < o.length; n++) {
				let r = o[n];
				if (r.pageNo !== u || r.rowNo !== 0) continue;
				let { leftTop: i, rightTop: a } = r.coordinate;
				if (t <= e[3] || t >= i[0] && t <= a[0] || o[n + 1]?.rowNo !== 0) return { index: r.index };
			}
			else {
				let n = _[_.length - 1];
				if (n) {
					let r = n.rowNo;
					for (let n = 0; n < o.length; n++) {
						let i = o[n];
						if (i.pageNo !== u || i.rowNo !== r) continue;
						let { leftTop: a, rightTop: s } = i.coordinate;
						if (t <= e[3] || t >= a[0] && t <= s[0] || o[n + 1]?.rowNo !== r) return { index: i.index };
					}
				}
			}
			return { index: _[_.length - 1]?.index || o.length - 1 };
		}
		return {
			hitLineStartIndex: p,
			index: f,
			isControl: !!a[f]?.controlId
		};
	}
	getFloatPositionByXY(e) {
		let { x: t, y: n } = e, r = e.pageNo ?? this.draw.getPageNo(), i = this.draw.getZone().getZone(), { scale: a } = this.options;
		for (let o = 0; o < this.floatPositionList.length; o++) {
			let { position: s, element: c, isTable: l, index: u, trIndex: d, tdIndex: f, tdValueIndex: p, zone: m, pageNo: h } = this.floatPositionList[o];
			if (r === h && c.type === H.IMAGE && c.imgDisplay && e.imgDisplays.includes(c.imgDisplay) && (!m || m === i)) {
				let { x: e, y: r } = this.getFloatPositionCoordinate(this.floatPositionList[o]), i = c.width * a, m = c.height * a;
				if (t >= e && t <= e + i && n >= r && n <= r + m) return l ? {
					index: u,
					isDirectHit: !0,
					isImage: !0,
					isTable: l,
					trIndex: d,
					tdIndex: f,
					tdValueIndex: p,
					tdId: c.tdId,
					trId: c.trId,
					tableId: c.tableId
				} : {
					index: s.index,
					isDirectHit: !0,
					isImage: !0
				};
			}
		}
	}
	adjustPositionContext(e) {
		let t = this.getPositionByXY(e);
		if (!~t.index) return null;
		if (t.isControl && this.draw.getMode() !== p.READONLY) {
			let { index: e, isTable: n, trIndex: r, tdIndex: i, tdValueIndex: a } = t, { newIndex: o } = this.draw.getControl().moveCursor({
				index: e,
				isTable: n,
				trIndex: r,
				tdIndex: i,
				tdValueIndex: a
			});
			n ? t.tdValueIndex = o : t.index = o;
		}
		let { index: n, isCheckbox: r, isRadio: i, isControl: a, isImage: o, isLabel: s, isDirectHit: c, isTable: l, trIndex: u, tdIndex: d, tdId: f, trId: m, tableId: h, tablePath: g } = t;
		return this.setPositionContext({
			isTable: l || !1,
			isCheckbox: r || !1,
			isRadio: i || !1,
			isControl: a || !1,
			isImage: o || !1,
			isLabel: s || !1,
			isDirectHit: c || !1,
			index: n,
			trIndex: u,
			tdIndex: d,
			tdId: f,
			trId: m,
			tableId: h,
			tablePath: g
		}), t;
	}
	setSurroundPosition(e) {
		let { scale: t } = this.options, { pageNo: n, row: r, rowElement: i, rowElementRect: a, surroundElementList: o, availableWidth: s } = e, c = a.x, l = 0;
		if (o.length && !Rn(i) && !i.control?.minWidth) for (let e = 0; e < o.length; e++) {
			let u = o[e], d = u.imgFloatPosition;
			if (d.pageNo !== n) continue;
			let f = {
				...d,
				x: d.x * t,
				y: d.y * t,
				width: u.width * t,
				height: u.height * t
			};
			if (ue(a, f)) {
				r.isSurround = !0;
				let e = f.width + f.x - a.x;
				if (i.left = e, r.width += e, l += e, c = f.x + f.width, r.width + i.metrics.width > s) {
					i.left = 0, r.width -= l;
					break;
				}
			}
		}
		return {
			x: c,
			rowIncreaseWidth: l
		};
	}
}, ei = class {
	draw;
	options;
	range;
	listener;
	eventBus;
	position;
	historyManager;
	defaultStyle;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.listener = e.getListener(), this.eventBus = e.getEventBus(), this.position = e.getPosition(), this.historyManager = e.getHistoryManager(), this.range = {
			startIndex: -1,
			endIndex: -1
		}, this.defaultStyle = null;
	}
	getRange() {
		return this.range;
	}
	clearRange() {
		this.setRange(-1, -1);
	}
	setDefaultStyle(e) {
		this.defaultStyle = e ? {
			...this.defaultStyle,
			...e
		} : null;
	}
	getDefaultStyle() {
		return this.defaultStyle;
	}
	getRangeAnchorStyle(e, t) {
		let n = On(e, t);
		return n ? {
			...n,
			...this.defaultStyle
		} : null;
	}
	getIsRangeChange(e, t, n, r, i, a, o) {
		return this.range.startIndex !== e || this.range.endIndex !== t || this.range.tableId !== n || this.range.startTdIndex !== r || this.range.endTdIndex !== i || this.range.startTrIndex !== a || this.range.endTrIndex !== o;
	}
	getIsCollapsed() {
		let { startIndex: e, endIndex: t } = this.range;
		return e === t;
	}
	getIsSelection() {
		let { startIndex: e, endIndex: t } = this.range;
		return !~e && !~t ? !1 : e !== t;
	}
	getSelection() {
		let { startIndex: e, endIndex: t } = this.range;
		if (e === t) return null;
		let n = this.draw.getElementList();
		return n.slice(n[e]?.value === "​" ? e : e + 1, t + 1);
	}
	getSelectionElementList() {
		if (this.range.isCrossRowCol) {
			let e = this.draw.getTableParticle().getRangeRowCol();
			if (!e) return null;
			let t = [];
			for (let n = 0; n < e.length; n++) {
				let r = e[n];
				for (let e = 0; e < r.length; e++) {
					let n = r[e];
					t.push(...n.value);
				}
			}
			return t;
		}
		return this.getSelection();
	}
	getTextLikeSelection() {
		let e = this.getSelection();
		return e ? e.filter((e) => !e.type || Be.includes(e.type)) : null;
	}
	getTextLikeSelectionElementList() {
		let e = this.getSelectionElementList();
		return e ? e.filter((e) => !e.type || Be.includes(e.type)) : null;
	}
	getRangeRow() {
		let { startIndex: e, endIndex: t } = this.range;
		if (!~e && !~t) return null;
		let n = this.position.getPositionList(), r = /* @__PURE__ */ new Map();
		for (let i = e; i < t + 1; i++) {
			let { pageNo: e, rowNo: t } = n[i], a = r.get(e);
			a ? a.has(t) || a.add(t) : r.set(e, /* @__PURE__ */ new Set([t]));
		}
		return r;
	}
	getRangeRowElementList() {
		let { startIndex: e, endIndex: t, isCrossRowCol: n } = this.range;
		if (!~e && !~t) return null;
		if (n) return this.getSelectionElementList();
		let r = this.getRangeRow();
		if (!r) return null;
		let i = this.position.getPositionList(), a = this.draw.getElementList(), o = [];
		for (let e = 0; e < i.length; e++) {
			let t = i[e], n = r.get(t.pageNo);
			n && n.has(t.rowNo) && o.push(a[e]);
		}
		return o;
	}
	getRangeParagraph() {
		let { startIndex: e, endIndex: t } = this.range;
		if (!~e && !~t) return null;
		let n = this.position.getPositionList(), r = this.draw.getElementList(), i = /* @__PURE__ */ new Map(), a = e;
		for (; a >= 0;) {
			let { pageNo: e, rowNo: t } = n[a], o = i.get(e);
			o || (o = [], i.set(e, o)), o.includes(t) || o.unshift(t);
			let s = r[a], c = r[a - 1];
			if (s.value === "​" && !s.listWrap || s.listId !== c?.listId || s.titleId !== c?.titleId) break;
			a--;
		}
		let o = e === t;
		if (!o) {
			let r = e + 1;
			for (; r < t;) {
				let { pageNo: e, rowNo: t } = n[r], a = i.get(e);
				a || (a = [], i.set(e, a)), a.includes(t) || a.push(t), r++;
			}
		}
		let s = t;
		for (o && r[e].value === "​" && (s += 1); s < n.length;) {
			let e = r[s], t = r[s + 1];
			if (e.value === "​" && !e.listWrap || e.listId !== t?.listId || e.titleId !== t?.titleId) break;
			let { pageNo: a, rowNo: o } = n[s], c = i.get(a);
			c || (c = [], i.set(a, c)), c.includes(o) || c.push(o), s++;
		}
		return i;
	}
	getRangeParagraphInfo() {
		let { startIndex: e, endIndex: t } = this.range;
		if (!~e && !~t) return null;
		let n = -1, r = [], i = this.getRangeParagraph();
		if (!i) return null;
		let a = this.draw.getElementList(), o = this.position.getPositionList();
		for (let e = 0; e < o.length; e++) {
			let t = o[e], s = i.get(t.pageNo);
			s && s.includes(t.rowNo) && (~n || (n = t.index), r.push(a[e]));
		}
		return r.length ? {
			elementList: r,
			startIndex: n
		} : null;
	}
	getRangeParagraphElementList() {
		return this.range.isCrossRowCol ? this.getSelectionElementList() : this.getRangeParagraphInfo()?.elementList || null;
	}
	getRangeTableElement() {
		let e = this.position.getPositionContext();
		return e.isTable ? this.draw.getOriginalElementList()[e.index] : null;
	}
	getIsSelectAll() {
		let e = this.draw.getElementList(), { startIndex: t, endIndex: n } = this.range;
		return t === 0 && e.length - 1 === n && !this.position.getPositionContext().isTable;
	}
	getIsPointInRange(e, t) {
		let { startIndex: n, endIndex: r } = this.range, i = this.position.getPositionList();
		for (let a = n + 1; a <= r && i[a]; a++) {
			let { coordinate: { leftTop: n, rightBottom: r } } = i[a];
			if (e >= n[0] && e <= r[0] && t >= n[1] && t <= r[1]) return !0;
		}
		return !1;
	}
	getKeywordRangeList(e) {
		let t = this.draw.getSearch().getMatchList(e, this.draw.getOriginalElementList()), n = /* @__PURE__ */ new Map();
		for (let e of t) {
			let t = n.get(e.groupId);
			if (t) t.endIndex += 1;
			else {
				let { type: t, groupId: r, tableId: i, index: a, tdIndex: o, trIndex: s } = e, c = {
					startIndex: a,
					endIndex: a
				};
				t === f.TABLE && (c.tableId = i, c.startTdIndex = o, c.endTdIndex = o, c.startTrIndex = s, c.endTrIndex = s), n.set(r, c);
			}
		}
		let r = [];
		return n.forEach((e) => {
			r.push(e);
		}), r;
	}
	getIsCanInput() {
		let { startIndex: e, endIndex: t } = this.getRange();
		if (!~e && !~t) return !1;
		let n = this.draw.getElementList(), r = n[e];
		if (e === t) return (r.controlComponent !== K.PRE_TEXT || n[e + 1]?.controlComponent !== K.PRE_TEXT) && r.controlComponent !== K.POST_TEXT;
		let i = n[t];
		return !r.controlId && !i.controlId || (!r.controlId || r.controlComponent === K.POSTFIX) && (!i.controlId || i.controlComponent === K.POSTFIX) || !!r.controlId && i.controlId === r.controlId && i.controlComponent !== K.PRE_TEXT && i.controlComponent !== K.POST_TEXT && i.controlComponent !== K.POSTFIX;
	}
	setRange(e, t, n, r, i, a, o) {
		let s = this.getIsRangeChange(e, t, n, r, i, a, o);
		s && (this.range.startIndex = e, this.range.endIndex = t, this.range.tableId = n, this.range.startTdIndex = r, this.range.endTdIndex = i, this.range.startTrIndex = a, this.range.endTrIndex = o, this.range.isCrossRowCol = !!(r || i || a || o), this.setDefaultStyle(null)), this.range.zone = this.draw.getZone().getZone();
		let c = this.draw.getControl();
		if (~e && ~t && this.draw.getElementList()[e]?.controlId) {
			c.initControl();
			return;
		}
		c.destroyControl(), s && this.eventBus.isSubscribe("rangeChange") && this.eventBus.emit("rangeChange", this.range);
	}
	replaceRange(e) {
		this.setRange(e.startIndex, e.endIndex, e.tableId, e.startTdIndex, e.endTdIndex, e.startTrIndex, e.endTrIndex);
	}
	shrinkRange() {
		let { startIndex: e, endIndex: t } = this.range;
		e === t || !~e && !~t || this.replaceRange({
			...this.range,
			startIndex: t
		});
	}
	setRangeStyle() {
		let e = this.listener.rangeStyleChange, t = this.eventBus.isSubscribe("rangeStyleChange");
		if (!e && !t) return;
		let { startIndex: n, endIndex: r, isCrossRowCol: i } = this.range;
		if (!~n && !~r) return;
		let a;
		if (i) a = this.draw.getOriginalElementList()[this.position.getPositionContext().index];
		else {
			let e = ~r ? r : 0, t = this.draw.getElementList();
			a = this.getRangeAnchorStyle(t, e);
		}
		if (!a) return;
		let o = this.getSelection() || [a], s = a.type || H.TEXT, c = a.font || this.options.defaultFont, l = a.size || this.options.defaultSize, u = !~o.findIndex((e) => !e.bold), d = !~o.findIndex((e) => !e.italic), f = !~o.findIndex((e) => !e.underline && !e.control?.underline), p = !~o.findIndex((e) => !e.strikeout), m = a.color || null, h = a.highlight || null, g = a.rowFlex || null, _ = a.rowMargin ?? this.options.defaultRowMargin, v = a.dashArray || [], y = a.level || null, b = a.listType || null, x = a.listStyle || null, S = f && a.textDecoration || null, C = !!this.draw.getPainterStyle(), w = {
			type: s,
			undo: this.historyManager.isCanUndo(),
			redo: this.historyManager.isCanRedo(),
			painter: C,
			font: c,
			size: l,
			bold: u,
			italic: d,
			underline: f,
			strikeout: p,
			color: m,
			highlight: h,
			rowFlex: g,
			rowMargin: _,
			dashArray: v,
			level: y,
			listType: b,
			listStyle: x,
			groupIds: a.groupIds || null,
			textDecoration: S,
			extension: a.extension ?? null
		};
		e && e(w), t && this.eventBus.emit("rangeStyleChange", w);
	}
	recoveryRangeStyle() {
		let e = this.listener.rangeStyleChange, t = this.eventBus.isSubscribe("rangeStyleChange");
		if (!e && !t) return;
		let n = this.options.defaultFont, r = this.options.defaultSize, i = this.options.defaultRowMargin, a = !!this.draw.getPainterStyle(), o = {
			type: null,
			undo: this.historyManager.isCanUndo(),
			redo: this.historyManager.isCanRedo(),
			painter: a,
			font: n,
			size: r,
			bold: !1,
			italic: !1,
			underline: !1,
			strikeout: !1,
			color: null,
			highlight: null,
			rowFlex: null,
			rowMargin: i,
			dashArray: [],
			level: null,
			listType: null,
			listStyle: null,
			groupIds: null,
			textDecoration: null,
			extension: null
		};
		e && e(o), t && this.eventBus.emit("rangeStyleChange", o);
	}
	shrinkBoundary(e = {}) {
		let t = e.elementList || this.draw.getElementList(), n = e.range || this.getRange(), { startIndex: r, endIndex: i } = n;
		if (!~r && !~i) return;
		let a = t[r], o = t[i];
		if (r === i) {
			if (a.controlComponent === K.PLACEHOLDER) {
				let e = r - 1;
				for (; e > 0;) {
					let r = t[e];
					if (r.controlId !== a.controlId || r.controlComponent === K.PREFIX || r.controlComponent === K.PRE_TEXT) {
						n.startIndex = e, n.endIndex = e;
						break;
					}
					e--;
				}
			}
		} else {
			if (a.controlComponent === K.PLACEHOLDER || o.controlComponent === K.PLACEHOLDER) {
				let e = i - 1;
				for (; e > 0;) {
					let r = t[e];
					if (r.controlId !== o.controlId || r.controlComponent === K.PREFIX || r.controlComponent === K.PRE_TEXT) {
						n.startIndex = e, n.endIndex = e;
						return;
					}
					e--;
				}
			}
			if (a.controlComponent === K.PREFIX) {
				let e = r + 1;
				for (; e < t.length;) {
					let r = t[e];
					if (r.controlId !== a.controlId || r.controlComponent === K.VALUE) {
						n.startIndex = e - 1;
						break;
					}
					if (r.controlComponent === K.PLACEHOLDER) {
						n.startIndex = e - 1, n.endIndex = e - 1;
						return;
					}
					e++;
				}
			}
			if (o.controlComponent !== K.VALUE) {
				let e = r - 1;
				for (; e > 0;) {
					let r = t[e];
					if (r.controlId !== a.controlId || r.controlComponent === K.VALUE) {
						n.startIndex = e;
						break;
					}
					if (r.controlComponent === K.PLACEHOLDER) {
						n.startIndex = e, n.endIndex = e;
						return;
					}
					e--;
				}
			}
		}
	}
	render(e, t, n, r, i) {
		e.save(), e.globalAlpha = this.options.rangeAlpha, e.fillStyle = this.options.rangeColor, e.fillRect(t, n, r, i), e.restore();
	}
	toString() {
		let e = this.getTextLikeSelection();
		return e ? e.filter((e) => !hn(e)).map((e) => e.value).join("").replace(/* @__PURE__ */ RegExp("​", "g"), "") : "";
	}
}, ti = class {
	draw;
	options;
	imageCache;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.imageCache = /* @__PURE__ */ new Map();
	}
	_renderBackgroundColor(e, t, n, r) {
		e.save(), e.fillStyle = t, e.fillRect(0, 0, n, r), e.restore();
	}
	_drawImage(e, t, n, r) {
		let { background: i, scale: a } = this.options;
		if (i.size === Mt.CONTAIN) {
			let o = t.width * a, s = t.height * a;
			if (!i.repeat || i.repeat === Nt.NO_REPEAT) e.drawImage(t, 0, 0, o, s);
			else {
				let c = 0, l = 0, u = i.repeat === Nt.REPEAT || i.repeat === Nt.REPEAT_X ? Math.ceil(n * a / o) : 1, d = i.repeat === Nt.REPEAT || i.repeat === Nt.REPEAT_Y ? Math.ceil(r * a / s) : 1;
				for (let n = 0; n < u; n++) {
					for (let n = 0; n < d; n++) e.drawImage(t, c, l, o, s), l += s;
					l = 0, c += o;
				}
			}
		} else e.drawImage(t, 0, 0, n * a, r * a);
	}
	_renderBackgroundImage(e, t, n) {
		let { background: r } = this.options, i = this.imageCache.get(r.image);
		if (i) this._drawImage(e, i, t, n);
		else {
			let i = new Image();
			i.setAttribute("crossOrigin", "Anonymous"), i.src = r.image, i.onload = () => {
				this.imageCache.set(r.image, i), this._drawImage(e, i, t, n), this.draw.render({
					isCompute: !1,
					isSubmitHistory: !1
				});
			};
		}
	}
	render(e, t) {
		let { background: { image: n, color: r, applyPageNumbers: i } } = this.options;
		if (n && (!i?.length || i.includes(t))) {
			let { width: t, height: n } = this.options;
			this._renderBackgroundImage(e, t, n);
		} else {
			let n = this.draw.getCanvasWidth(t), i = this.draw.getCanvasHeight(t);
			this._renderBackgroundColor(e, r, n, i);
		}
	}
}, ni = class {
	fillRect;
	fillColor;
	fillDecorationStyle;
	constructor() {
		this.fillRect = this.clearFillInfo();
	}
	clearFillInfo() {
		return this.fillColor = void 0, this.fillDecorationStyle = void 0, this.fillRect = {
			x: 0,
			y: 0,
			width: 0,
			height: 0
		}, this.fillRect;
	}
	recordFillInfo(e, t, n, r, i, a, o) {
		let s = !this.fillRect.width;
		if (!s && (this.fillColor !== a || this.fillDecorationStyle !== o)) {
			this.render(e), this.clearFillInfo(), this.recordFillInfo(e, t, n, r, i, a, o);
			return;
		}
		s && (this.fillRect.x = t, this.fillRect.y = n), i && this.fillRect.height < i && (this.fillRect.height = i), this.fillRect.width += r, this.fillColor = a, this.fillDecorationStyle = o;
	}
}, ri = class extends ni {
	options;
	constructor(e) {
		super(), this.options = e.getOptions();
	}
	render(e) {
		if (!this.fillRect.width) return;
		let { highlightAlpha: t } = this.options, { x: n, y: r, width: i, height: a } = this.fillRect;
		e.save(), e.globalAlpha = t, e.fillStyle = this.fillColor, e.fillRect(n, r, i, a), e.restore(), this.clearFillInfo();
	}
}, ii = class {
	draw;
	options;
	constructor(e) {
		this.draw = e, this.options = e.getOptions();
	}
	render(e, t) {
		let { marginIndicatorColor: n, pageMode: r } = this.options, { width: i, height: a, margins: o } = this.draw.getPageSize(t), s = r === h.CONTINUITY ? this.draw.getCanvasHeight(t) / this.draw.getPagePixelRatio() : a, c = this.draw.getMarginIndicatorSize();
		e.save(), e.translate(.5, .5), e.strokeStyle = n, e.beginPath();
		let l = [o[3], o[0]], u = [i - o[1], o[0]], d = [o[3], s - o[2]], f = [i - o[1], s - o[2]];
		e.moveTo(l[0] - c, l[1]), e.lineTo(...l), e.lineTo(l[0], l[1] - c), e.moveTo(u[0] + c, u[1]), e.lineTo(...u), e.lineTo(u[0], u[1] - c), e.moveTo(d[0] - c, d[1]), e.lineTo(...d), e.lineTo(d[0], d[1] + c), e.moveTo(f[0] + c, f[1]), e.lineTo(...f), e.lineTo(f[0], f[1] + c), e.stroke(), e.restore();
	}
}, ai = class {
	draw;
	options;
	position;
	range;
	searchKeyword;
	searchNavigateIndex;
	searchOptions;
	searchMatchList;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.position = e.getPosition(), this.range = e.getRange(), this.searchNavigateIndex = null, this.searchOptions = null, this.searchKeyword = null, this.searchMatchList = [];
	}
	getSearchKeyword() {
		return this.searchKeyword;
	}
	setSearchKeyword(e, t) {
		this.searchKeyword = e, this.searchNavigateIndex = null, this.searchOptions = t || null;
	}
	getSearchMatchGroupStartIndex(e) {
		let t = this.searchMatchList[e];
		if (!t) return null;
		let n = e;
		for (; n > 0 && this.searchMatchList[n - 1].groupId === t.groupId;) n--;
		return n;
	}
	searchNavigatePre() {
		if (!this.searchMatchList.length || !this.searchKeyword) return null;
		if (this.searchNavigateIndex === null) this.searchNavigateIndex = 0;
		else {
			let e = this.searchNavigateIndex - 1, t = !1, n = this.searchMatchList[this.searchNavigateIndex].groupId;
			for (; e >= 0;) {
				if (n !== this.searchMatchList[e].groupId) {
					t = !0, this.searchNavigateIndex = this.getSearchMatchGroupStartIndex(e);
					break;
				}
				e--;
			}
			if (!t) {
				if (this.searchMatchList[this.searchMatchList.length - 1].groupId === n) return null;
				this.searchNavigateIndex = this.getSearchMatchGroupStartIndex(this.searchMatchList.length - 1);
			}
		}
		return this.searchNavigateIndex;
	}
	searchNavigateNext() {
		if (!this.searchMatchList.length || !this.searchKeyword) return null;
		if (this.searchNavigateIndex === null) this.searchNavigateIndex = 0;
		else {
			let e = this.searchNavigateIndex + 1, t = !1, n = this.searchMatchList[this.searchNavigateIndex].groupId;
			for (; e < this.searchMatchList.length;) {
				if (n !== this.searchMatchList[e].groupId) {
					t = !0, this.searchNavigateIndex = e;
					break;
				}
				e++;
			}
			if (!t) {
				if (this.searchMatchList[0].groupId === n) return null;
				this.searchNavigateIndex = 0;
			}
		}
		return this.searchNavigateIndex;
	}
	searchNavigateScrollIntoView(e) {
		let { coordinate: { leftTop: t, leftBottom: n, rightTop: r }, pageNo: i } = e, { x: a, y: o } = this.draw.getPageOffset(i), s = document.createElement("div");
		s.style.position = "absolute", s.style.width = `${r[0] - t[0] + 50}px`, s.style.height = `${n[1] - t[1] + 50}px`, s.style.left = `${t[0] + a}px`, s.style.top = `${t[1] + o}px`, this.draw.getContainer().append(s), s.scrollIntoView(!1), s.remove();
	}
	getSearchNavigateIndexList() {
		if (this.searchNavigateIndex === null || !this.searchKeyword) return [];
		let e = this.searchMatchList[this.searchNavigateIndex];
		if (!e) return [];
		let t = [], n = this.searchNavigateIndex;
		for (; n < this.searchMatchList.length && this.searchMatchList[n].groupId === e.groupId;) t.push(n), n++;
		return t;
	}
	getSearchMatchList() {
		return this.searchMatchList;
	}
	getSearchNavigateInfo() {
		if (!this.searchKeyword || !this.searchMatchList.length) return null;
		let e = this.searchNavigateIndex === null ? null : this.searchMatchList[this.searchNavigateIndex]?.groupId, t = 0, n = 0, r = null;
		for (let i = 0; i < this.searchMatchList.length; i++) {
			let a = this.searchMatchList[i];
			r !== a.groupId && (r = a.groupId, n += 1, e === r && (t = n));
		}
		return {
			index: t,
			count: n
		};
	}
	getMatchList(e, t) {
		let { isRegEnable: n = !1, isIgnoreCase: r = !0 } = this.searchOptions || {}, i = r ? e.toLocaleLowerCase() : e, a = [], o = [], s = t.length, c = [];
		for (let e = 0; e < s; e++) t[e].type === H.TABLE && c.push(e);
		let l = 0, u = 0;
		for (; u < s - 1;) {
			let e = c.length ? c[l] : s, n = t.slice(u, e);
			n.length && o.push({
				index: u,
				type: f.PAGE,
				elementList: n
			});
			let r = t[e];
			r && o.push({
				index: e,
				type: f.TABLE,
				elementList: [r]
			}), u = e + 1, l++;
		}
		let d = this.draw.getTraceParticle();
		function p(e, t, i, o) {
			if (!e) return;
			let s = i.map((e) => !e.type || Be.includes(e.type) && e.controlComponent !== K.CHECKBOX && e.controlComponent !== K.RADIO && !e.hide && !e.control?.hide && !e.area?.hide && !d.isTraceHidden(e) ? e.value : "​").filter(Boolean).join("");
			r && (s = s.toLocaleLowerCase());
			let c = [], l = n ? new RegExp(e) : e, { index: u, length: f } = me(s, l);
			for (; u !== -1 && f !== 0;) {
				c.push({
					index: u,
					length: f
				});
				let e = me(s, l, u + f);
				u = e.index, f = e.length;
			}
			for (let e = 0; e < c.length; e++) {
				let { index: n, length: r } = c[e], i = M();
				for (let e = 0; e < r; e++) {
					let r = n + e + (o?.startIndex || 0);
					a.push({
						type: t,
						index: r,
						groupId: i,
						...o
					});
				}
			}
		}
		for (let e = 0; e < o.length; e++) {
			let t = o[e];
			if (t.type === f.TABLE) {
				let e = t.elementList[0];
				for (let n = 0; n < e.trList.length; n++) {
					let r = e.trList[n];
					for (let a = 0; a < r.tdList.length; a++) {
						let o = r.tdList[a], s = {
							tableId: e.id,
							tableIndex: t.index,
							trIndex: n,
							tdIndex: a,
							tdId: o.id
						};
						p(i, t.type, o.value, s);
					}
				}
			} else p(i, t.type, t.elementList, { startIndex: t.index });
		}
		return a;
	}
	compute(e) {
		let t = this.searchOptions?.isLimitSelection && !this.range.getIsCollapsed(), n = t ? this.range.getSelectionElementList() : this.draw.getOriginalElementList();
		if (!n?.length || (this.searchMatchList = this.getMatchList(e, n), !t || !this.searchMatchList.length)) return;
		let { startIndex: r } = this.range.getRange(), i = r + 1;
		for (let e of this.searchMatchList) e.type === f.TABLE ? e.tableIndex += i : e.index += i;
	}
	render(e, t) {
		if (!this.searchMatchList || !this.searchMatchList.length || !this.searchKeyword) return;
		let { searchMatchAlpha: n, searchMatchColor: r, searchNavigateMatchColor: i } = this.options, a = this.position.getOriginalPositionList(), o = this.draw.getOriginalElementList();
		e.save(), e.globalAlpha = n;
		for (let n = 0; n < this.searchMatchList.length; n++) {
			let s = this.searchMatchList[n], c = null;
			if (s.type === f.TABLE) {
				let { tableIndex: e, trIndex: t, tdIndex: n, index: r } = s;
				c = o[e]?.trList[t].tdList[n]?.positionList[r];
			} else c = a[s.index];
			if (!c) continue;
			let { coordinate: { leftTop: l, leftBottom: u, rightTop: d }, pageNo: p } = c;
			if (p !== t) continue;
			if (this.getSearchNavigateIndexList().includes(n)) {
				e.fillStyle = i;
				let t = this.searchMatchList[n - 1];
				(!t || t.groupId !== s.groupId) && this.searchNavigateScrollIntoView(c);
			} else e.fillStyle = r;
			let m = l[0], h = l[1], g = d[0] - l[0], _ = u[1] - l[1];
			e.fillRect(m, h, g, _);
		}
		e.restore();
	}
	replace(e, t) {
		if (this.draw.isReadonly() || e == null) return;
		let n = this.getSearchMatchList(), r = t?.index;
		if (L(r)) {
			let e = [];
			n.forEach((t) => {
				let n = e[e.length - 1];
				!n || n[0].groupId !== t.groupId ? e.push([t]) : n.push(t);
			}), n = e[r];
		}
		if (!n?.length) return;
		let i = this.draw.isDesignMode();
		if (!this.draw.getOptions().trace.disabled) {
			this.replaceWithTrace(e, n);
			return;
		}
		let a = 0, o = 0, s = "", c = "", l = -1, u = this.draw.getOriginalElementList();
		for (let t = 0; t < n.length; t++) {
			let r = n[t];
			if (r.type === f.TABLE) {
				let { tableIndex: n, trIndex: d, tdIndex: f, index: p, tdId: m } = r;
				c && m !== c && (o = 0), c = m;
				let h = u[n + a].trList[d].tdList[f].value, g = p + o, _ = h[g];
				if (!i && (_?.control?.deletable === !1 || _?.title?.deletable === !1)) continue;
				if (e === "") {
					this.draw.spliceElementList(h, g, 1), o--, ~l || (l = t);
					continue;
				}
				if (s === r.groupId) {
					this.draw.spliceElementList(h, g, 1), o--;
					continue;
				}
				~l || (l = t);
				for (let t = 0; t < e.length; t++) {
					let n = e[t];
					t === 0 ? _.value = n : (this.draw.spliceElementList(h, g + t, 0, [{
						..._,
						value: n
					}]), o++);
				}
			} else {
				let n = r.index + a, o = u[n];
				if (!i && (o?.control?.deletable === !1 || o?.title?.deletable === !1) || o.type === H.CONTROL && o.controlComponent !== K.VALUE) continue;
				if (e === "") {
					this.draw.spliceElementList(u, n, 1), a--, ~l || (l = t);
					continue;
				}
				if (~l || (l = t), s === r.groupId) {
					this.draw.spliceElementList(u, n, 1), a--;
					continue;
				}
				for (let t = 0; t < e.length; t++) {
					let r = e[t];
					t === 0 ? o.value = r : (this.draw.spliceElementList(u, n + t, 0, [{
						...o,
						value: r
					}]), a++);
				}
			}
			s = r.groupId;
		}
		if (!~l) return;
		let d = n[l], p = d.index + (e.length - 1);
		if (d.type === f.TABLE) {
			let { tableIndex: e, trIndex: t, tdIndex: n, index: r } = d, i = u[e].trList[t].tdList[n].value[r];
			this.position.setPositionContext({
				isTable: !0,
				index: e,
				trIndex: t,
				tdIndex: n,
				tdId: i.tdId,
				trId: i.trId,
				tableId: i.tableId
			});
		} else this.position.setPositionContext({ isTable: !1 });
		this.draw.getRange().setRange(p, p), this.draw.render({ curIndex: p });
	}
	replaceWithTrace(e, t) {
		let n = [];
		for (let e of t) {
			let t = n[n.length - 1];
			!t || t[0].groupId !== e.groupId ? n.push([e]) : t.push(e);
		}
		let r = this.draw.getOriginalElementList(), i = null, a = -1;
		for (let t = n.length - 1; t >= 0; t--) {
			let o = n[t], s = o[0], c, l = !0;
			if (s.type === f.TABLE) {
				let { tableIndex: e, trIndex: t, tdIndex: n } = s, i = r[e].trList[t].tdList[n];
				c = i.value, l = i.deletable !== !1;
			} else c = r;
			let u = s.index;
			if (c.slice(u, u + o.length).some((e) => e.type === H.CONTROL && e.controlComponent !== K.VALUE)) continue;
			let d = (this.draw.deleteElementList(c, u, o.length, { tdDeletable: l }) || [])[0];
			if (!d) continue;
			let p = c.indexOf(d, u);
			if (e) {
				let t = e.split("").map((e) => {
					let t = {
						...d,
						value: e
					};
					return delete t.trace, t;
				});
				this.draw.getTraceParticle().markElementListInserted(t), this.draw.spliceElementList(c, p, 0, t);
			}
			i = s, a = e ? p + e.length - 1 : Math.max(p - 1, 0);
		}
		if (i) {
			if (i.type === f.TABLE) {
				let { tableIndex: e, trIndex: t, tdIndex: n, tdId: a, tableId: o } = i;
				this.position.setPositionContext({
					isTable: !0,
					index: e,
					trIndex: t,
					tdIndex: n,
					tdId: a,
					trId: r[e].trList[t].id,
					tableId: o
				});
			} else this.position.setPositionContext({ isTable: !1 });
			this.draw.getRange().setRange(a, a), this.draw.render({ curIndex: a });
		}
	}
}, oi = class {
	options;
	draw;
	position;
	segmenter;
	spellcheckRangeList;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.position = e.getPosition(), this.segmenter = null, this.spellcheckRangeList = [];
	}
	_isElementHidden(e) {
		return !!(e.hide || e.control?.hide || e.area?.hide || this.draw.getTraceParticle().isTraceHidden(e));
	}
	getSpellcheckRangeList() {
		return this.options.spellcheck.disabled && (this.spellcheckRangeList = []), this.spellcheckRangeList;
	}
	_appendWordList(e, t, n, r, i) {
		if (!this.segmenter) return;
		let a = [], o = [], s = 0;
		for (let r = t; r < n; r++) {
			let t = e[r], n = !this._isElementHidden(t) && (!t.type || t.type !== H.CONTROL && Be.includes(t.type)) ? t.value : "​";
			a.push(n), s += n.length, o.push(s - 1);
		}
		let c = a.join(""), l = 0;
		for (let { segment: e, index: n, isWordLike: a } of this.segmenter.segment(c)) {
			if (!a) continue;
			for (; o[l] < n;) l++;
			let s = l, c = n + e.length - 1;
			for (; o[l] < c;) l++;
			r.push({
				word: e,
				startIndex: t + s,
				endIndex: t + l,
				...i
			});
		}
	}
	_collectWordList(e, t, n) {
		let r = 0;
		for (let i = 0; i < e.length; i++) {
			let a = e[i];
			if (a.type === H.TABLE) {
				if (this._appendWordList(e, r, i, t, n), !this._isElementHidden(a)) {
					let e = a.trList || [];
					for (let r = 0; r < e.length; r++) {
						let o = e[r], s = o.tdList;
						for (let e = 0; e < s.length; e++) {
							let c = s[e], l = [...n?.tablePath || [], {
								index: i,
								trIndex: r,
								tdIndex: e,
								tdId: c.id,
								trId: o.id,
								tableId: a.id
							}];
							this._collectWordList(c.value, t, {
								tableId: a.id,
								tableIndex: l[0].index,
								trIndex: r,
								tdIndex: e,
								tablePath: l
							});
						}
					}
				}
				r = i + 1;
			}
		}
		this._appendWordList(e, r, e.length, t, n);
	}
	getSpellcheckWordList() {
		if (this.options.spellcheck.disabled || (!this.segmenter && Intl.Segmenter && (this.segmenter = new Intl.Segmenter(void 0, { granularity: "word" })), !this.segmenter)) return [];
		let e = this.draw.getOriginalMainElementList(), t = [];
		return this._collectWordList(e, t), t;
	}
	setSpellcheckRangeList(e) {
		let t = !this.options.spellcheck.disabled && e ? e.filter((e) => {
			let t = e.tableId === void 0 && e.tableIndex === void 0 && e.trIndex === void 0 && e.tdIndex === void 0 || typeof e.tableId == "string" && Number.isInteger(e.tableIndex) && Number.isInteger(e.trIndex) && Number.isInteger(e.tdIndex);
			return Number.isInteger(e.startIndex) && Number.isInteger(e.endIndex) && e.startIndex >= 0 && e.startIndex <= e.endIndex && t;
		}) : [];
		return !t.length && !this.spellcheckRangeList.length ? !1 : (this.spellcheckRangeList = t, !0);
	}
	_isSameTablePath(e, t) {
		if (!e) return !0;
		if (!t || e.length !== t.length) return !1;
		for (let n = 0; n < e.length; n++) {
			let r = e[n], i = t[n];
			if (r.index !== i.index || r.trIndex !== i.trIndex || r.tdIndex !== i.tdIndex || r.tableId !== i.tableId) return !1;
		}
		return !0;
	}
	getRangeByIndex(e, t) {
		if (this.options.spellcheck.disabled) return null;
		for (let n of this.spellcheckRangeList) if (n.tableId === t?.tableId && n.tableIndex === t?.tableIndex && n.trIndex === t?.trIndex && n.tdIndex === t?.tdIndex && this._isSameTablePath(n.tablePath, t?.tablePath) && !(e < n.startIndex || e > n.endIndex)) return n;
		return null;
	}
	_drawWave(e, t, n, r) {
		if (r <= 0) return;
		let { scale: i } = this.options, a = 1.2 * i, o = n + a, s = 2 * i, c = t + r, l = t, u = 1;
		for (e.beginPath(), e.moveTo(l, o); l < c;) {
			let t = Math.min(l + s, c);
			e.quadraticCurveTo((l + t) / 2, o + a * u, t, o), u *= -1, l = t;
		}
		e.stroke();
	}
	render(e, t) {
		if (this.options.spellcheck.disabled || !this.spellcheckRangeList.length) return;
		let n = this.position.getOriginalMainPositionList(), r = this.draw.getOriginalMainElementList();
		e.save(), e.strokeStyle = this.options.spellcheck.color, e.lineWidth = this.options.scale;
		for (let i of this.spellcheckRangeList) {
			let a = n;
			if (i.tableIndex !== void 0 && (a = this.position.getTableTdByContext(r, {
				isTable: !0,
				index: i.tableIndex,
				tableId: i.tableId,
				trIndex: i.trIndex,
				tdIndex: i.tdIndex,
				tablePath: i.tablePath
			})?.positionList || []), i.startIndex >= a.length) continue;
			let o = Math.min(i.endIndex, a.length - 1), s = a[i.startIndex]?.pageNo, c = a[o]?.pageNo;
			if (L(s) && L(c) && (t < s || t > c)) continue;
			let l = -1, u = 0, d = 0, f = () => {
				~l && (this._drawWave(e, l, u, d - l), l = -1);
			};
			for (let e = i.startIndex; e <= o; e++) {
				let n = a[e];
				if (!n) continue;
				let { pageNo: r, ascent: i, metrics: { boundingBoxDescent: o }, coordinate: { leftTop: s, rightTop: c } } = n;
				if (r !== t) {
					f();
					continue;
				}
				let p = s[1] + i + o;
				~l ? p === u ? d = c[0] : (f(), l = s[0], u = p, d = c[0]) : (l = s[0], u = p, d = c[0]);
			}
			f();
		}
		e.restore();
	}
}, si = class extends ni {
	options;
	constructor(e) {
		super(), this.options = e.getOptions();
	}
	render(e) {
		if (!this.fillRect.width) return;
		let { scale: t, strikeoutColor: n } = this.options, { x: r, y: i, width: a } = this.fillRect;
		e.save(), e.lineWidth = t, e.strokeStyle = this.fillColor || n;
		let o = i + .5;
		e.beginPath(), e.moveTo(r, o), e.lineTo(r + a, o), e.stroke(), e.restore(), this.clearFillInfo();
	}
}, ci;
(function(e) {
	e.SOLID = "solid", e.DOUBLE = "double", e.DASHED = "dashed", e.DOTTED = "dotted", e.WAVY = "wavy";
})(ci ||= {});
var li;
(function(e) {
	e.SOLID = "solid", e.DASHED = "dashed", e.DOTTED = "dotted";
})(li ||= {});
//#endregion
//#region src/editor/core/draw/richtext/Underline.ts
var ui = class extends ni {
	options;
	constructor(e) {
		super(), this.options = e.getOptions();
	}
	_drawLine(e, t, n, r, i) {
		let a = t + r;
		switch (e.beginPath(), i) {
			case li.DASHED:
				e.setLineDash([3, 1]);
				break;
			case li.DOTTED: e.setLineDash([1, 1]);
		}
		e.moveTo(t, n), e.lineTo(a, n), e.stroke();
	}
	_drawDouble(e, t, n, r) {
		let i = t + r, a = n + 3 * this.options.scale;
		e.beginPath(), e.moveTo(t, n), e.lineTo(i, n), e.stroke(), e.beginPath(), e.moveTo(t, a), e.lineTo(i, a), e.stroke();
	}
	_drawWave(e, t, n, r) {
		let { scale: i } = this.options, a = 1.2 * i, o = 1 / i, s = n + 2 * a;
		e.beginPath();
		for (let n = 0; n < r; n++) {
			let r = a * Math.sin(o * n);
			e.lineTo(t + n, s + r);
		}
		e.stroke();
	}
	render(e) {
		if (!this.fillRect.width) return;
		let { underlineColor: t, scale: n } = this.options, { x: r, y: i, width: a } = this.fillRect;
		e.save(), e.strokeStyle = this.fillColor || t, e.lineWidth = n;
		let o = Math.floor(i + 2 * e.lineWidth) + .5;
		switch (this.fillDecorationStyle) {
			case ci.WAVY:
				this._drawWave(e, r, o, a);
				break;
			case ci.DOUBLE:
				this._drawDouble(e, r, o, a);
				break;
			case ci.DASHED:
				this._drawLine(e, r, o, a, li.DASHED);
				break;
			case ci.DOTTED:
				this._drawLine(e, r, o, a, li.DOTTED);
				break;
			default: this._drawLine(e, r, o, a);
		}
		e.restore(), this.clearFillInfo();
	}
}, di = class {
	draw;
	options;
	ctx;
	curX;
	curY;
	text;
	curStyle;
	curColor;
	cacheMeasureText;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.ctx = e.getCtx(), this.curX = -1, this.curY = -1, this.text = "", this.curStyle = "", this.cacheMeasureText = /* @__PURE__ */ new Map();
	}
	measureBasisWord(e, t) {
		e.save(), e.font = t;
		let n = this.measureText(e, { value: "中" });
		return e.restore(), n;
	}
	measureWord(e, t, n) {
		let r = this.draw.getLetterReg(), i = 0, a = null, o = n;
		for (; o < t.length;) {
			let n = t[o];
			if (n.type && n.type !== H.TEXT || !r.test(n.value)) {
				a = n;
				break;
			}
			i += this.measureText(e, n).width, o++;
		}
		return {
			width: i,
			endElement: a
		};
	}
	measurePunctuationWidth(e, t) {
		return !t || !s.includes(t.value) ? 0 : (e.font = this.draw.getElementFont(t), this.measureText(e, t).width);
	}
	measureText(e, t) {
		if (t.width) {
			let n = e.measureText(t.value);
			return {
				width: t.width,
				actualBoundingBoxAscent: n.actualBoundingBoxAscent,
				actualBoundingBoxDescent: n.actualBoundingBoxDescent,
				actualBoundingBoxLeft: n.actualBoundingBoxLeft,
				actualBoundingBoxRight: n.actualBoundingBoxRight,
				fontBoundingBoxAscent: n.fontBoundingBoxAscent,
				fontBoundingBoxDescent: n.fontBoundingBoxDescent
			};
		}
		let n = `${t.value}${e.font}`, r = this.cacheMeasureText.get(n);
		if (r) return r;
		let i = e.measureText(t.value);
		return this.cacheMeasureText.set(n, i), i;
	}
	getBasisWordBoundingBoxAscent(e, t) {
		return this.measureBasisWord(e, t).actualBoundingBoxAscent;
	}
	complete() {
		this._render(), this.text = "";
	}
	record(e, t, n, r) {
		if (this.ctx = e, this.options.renderMode === v.COMPATIBILITY) {
			this._setCurXY(n, r), this.text = t.value, this.curStyle = t.style, this.curColor = t.color, this.complete();
			return;
		}
		this.text || this._setCurXY(n, r), (this.curStyle && t.style !== this.curStyle || t.color !== this.curColor) && (this.complete(), this._setCurXY(n, r)), this.text += t.value, this.curStyle = t.style, this.curColor = t.color;
	}
	_setCurXY(e, t) {
		this.curX = e, this.curY = t;
	}
	_render() {
		!this.text || !~this.curX || !~this.curY || (this.ctx.save(), this.ctx.font = this.curStyle, this.ctx.fillStyle = this.curColor || this.options.defaultColor, this.ctx.fillText(this.text, this.curX, this.curY), this.ctx.restore());
	}
}, fi = class e {
	draw;
	options;
	constructor(e) {
		this.draw = e, this.options = e.getOptions();
	}
	static formatNumberPlaceholder(e, t, r, i) {
		let a = i === n.CHINESE ? z(t) : `${t}`;
		return e.replace(r, a);
	}
	render(t, n) {
		let { scale: r, pageNumber: { size: i, font: a, color: o, rowFlex: s, numberType: c, format: l, startPageNo: d, fromPageNo: f } } = this.options;
		if (n < f) return;
		let p = l, m = new RegExp(Wt.PAGE_NO);
		m.test(p) && (p = e.formatNumberPlaceholder(p, n + d - f, m, c));
		let h = new RegExp(Wt.PAGE_COUNT);
		h.test(p) && (p = e.formatNumberPlaceholder(p, this.draw.getPageCount() - f, h, c));
		let { width: g, height: _, margins: v } = this.draw.getPageSize(n), y = _ - this.draw.getPageNumberBottom();
		t.save(), t.fillStyle = o, t.font = `${i * r}px ${a}`;
		let b = 0, { width: x } = t.measureText(p);
		b = s === u.CENTER ? (g - x) / 2 : s === u.RIGHT ? g - x - v[1] : v[3], t.fillText(p, b, y), t.restore();
	}
}, pi = class {
	draw;
	options;
	scrollContainer;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.scrollContainer = this.getScrollContainer(), setTimeout(() => {
			window.scrollY || this._observer();
		}), this._addEvent();
	}
	getScrollContainer() {
		return this.options.scrollContainerSelector && document.querySelector(this.options.scrollContainerSelector) || document;
	}
	_addEvent() {
		this.scrollContainer.addEventListener("scroll", this._observer);
	}
	removeEvent() {
		this.scrollContainer.removeEventListener("scroll", this._observer);
	}
	getElementVisibleInfo(e) {
		let t = e.getBoundingClientRect(), n = this.scrollContainer === document ? Math.max(document.documentElement.clientHeight, window.innerHeight) : this.scrollContainer.clientHeight, r = Math.min(t.bottom, n) - Math.max(t.top, 0);
		return { intersectionHeight: r > 0 ? r : 0 };
	}
	getPageVisibleInfo() {
		let e = this.draw.getPageList(), t = [], n = 0, r = 0;
		for (let i = 0; i < e.length; i++) {
			let a = e[i], { intersectionHeight: o } = this.getElementVisibleInfo(a);
			if (r && !o) break;
			o && t.push(i), o > r && (r = o, n = i);
		}
		return {
			intersectionPageNo: n,
			visiblePageNoList: t
		};
	}
	_observer = E(() => {
		let { intersectionPageNo: e, visiblePageNoList: t } = this.getPageVisibleInfo();
		this.draw.setIntersectionPageNo(e), this.draw.setVisiblePageNoList(t);
	}, 150);
}, mi = class {
	step = 5;
	thresholdPoints = [
		70,
		40,
		10,
		20
	];
	selectionContainer;
	rangeManager;
	requestAnimationFrameId;
	isMousedown;
	isMoving;
	clientWidth;
	clientHeight;
	containerRect;
	pageContainer;
	constructor(e) {
		this.rangeManager = e.getRange(), this.pageContainer = e.getPageContainer();
		let { scrollContainerSelector: t } = e.getOptions();
		this.selectionContainer = t && document.querySelector(t) || document, this.requestAnimationFrameId = null, this.isMousedown = !1, this.isMoving = !1, this.clientWidth = 0, this.clientHeight = 0, this.containerRect = null, this._addEvent();
	}
	_addEvent() {
		let e = this.selectionContainer;
		e.addEventListener("mousedown", this._mousedown), e.addEventListener("mousemove", this._mousemove), e.addEventListener("mouseup", this._mouseup), document.addEventListener("mouseleave", this._mouseup);
	}
	removeEvent() {
		let e = this.selectionContainer;
		e.removeEventListener("mousedown", this._mousedown), e.removeEventListener("mousemove", this._mousemove), e.removeEventListener("mouseup", this._mouseup), document.removeEventListener("mouseleave", this._mouseup);
	}
	_mousedown = () => {
		if (this.isMousedown = !0, this.clientWidth = this.selectionContainer instanceof Document ? document.documentElement.clientWidth : this.selectionContainer.clientWidth, this.clientHeight = this.selectionContainer instanceof Document ? document.documentElement.clientHeight : this.selectionContainer.clientHeight, !(this.selectionContainer instanceof Document)) {
			let e = this.selectionContainer.getBoundingClientRect();
			this.containerRect = e;
		}
	};
	_mouseup = () => {
		this.isMousedown = !1, this._stopMove();
	};
	_mousemove = (e) => {
		if (!this.isMousedown || this.rangeManager.getIsCollapsed() || !this.pageContainer.contains(e.target)) return;
		let { x: t, y: n } = e;
		this.containerRect && (t -= this.containerRect.x, n -= this.containerRect.y), n < this.thresholdPoints[0] ? this._startMove(be.UP) : this.clientHeight - n <= this.thresholdPoints[1] ? this._startMove(be.DOWN) : t < this.thresholdPoints[2] ? this._startMove(be.LEFT) : this.clientWidth - t < this.thresholdPoints[3] ? this._startMove(be.RIGHT) : this._stopMove();
	};
	_move(e) {
		let t = this.selectionContainer instanceof Document ? window : this.selectionContainer, n = this.selectionContainer instanceof Document ? window.scrollX : t.scrollLeft, r = this.selectionContainer instanceof Document ? window.scrollY : t.scrollTop;
		e === be.DOWN ? t.scrollTo(n, r + this.step) : e === be.UP ? t.scrollTo(n, r - this.step) : e === be.LEFT ? t.scrollTo(n - this.step, r) : t.scrollTo(n + this.step, r), this.requestAnimationFrameId = window.requestAnimationFrame(this._move.bind(this, e));
	}
	_startMove(e) {
		this.isMoving || (this.isMoving = !0, this._move(e));
	}
	_stopMove() {
		this.requestAnimationFrameId && (window.cancelAnimationFrame(this.requestAnimationFrameId), this.requestAnimationFrameId = null, this.isMoving = !1);
	}
}, hi = class {
	draw;
	range;
	options;
	fragmentContentHeightCache;
	tdLineHeightPrefixCache;
	fragmentTdListCache;
	constructor(e) {
		this.draw = e, this.range = e.getRange(), this.options = e.getOptions(), this.fragmentContentHeightCache = /* @__PURE__ */ new WeakMap(), this.tdLineHeightPrefixCache = /* @__PURE__ */ new WeakMap(), this.fragmentTdListCache = /* @__PURE__ */ new WeakMap();
	}
	getTrListGroupByCol(e) {
		let t = k(e);
		for (let n = 0; n < e.length; n++) {
			let e = t[n];
			for (let r = e.tdList.length - 1; r >= 0; r--) {
				let { rowspan: i, rowIndex: a, colIndex: o } = e.tdList[r], s = a + i - 1;
				if (s !== n) {
					let n = e.tdList.splice(r, 1)[0];
					t[s]?.tdList.splice(o, 0, n);
				}
			}
		}
		return t;
	}
	getRangeRowCol() {
		let e = this.draw.getPosition(), t = e.getPositionContext(), { isTable: n, trIndex: r, tdIndex: i } = t;
		if (!n) return null;
		let { isCrossRowCol: a, startTdIndex: o, endTdIndex: s, startTrIndex: c, endTrIndex: l } = this.range.getRange(), u = this.draw.getOriginalElementList(), d = e.getTableElementByContext(u, t);
		if (!d) return null;
		let f = d.trList;
		if (!a) return [[f[r].tdList[i]]];
		let p = f[c].tdList[o], m = f[l].tdList[s];
		(p.x > m.x || p.y > m.y) && ([p, m] = [m, p]);
		let h = p.colIndex, g = m.colIndex + (m.colspan - 1), _ = p.rowIndex, v = m.rowIndex + (m.rowspan - 1), y = [];
		for (let e = 0; e < f.length; e++) {
			let t = f[e], n = [];
			for (let e = 0; e < t.tdList.length; e++) {
				let r = t.tdList[e], i = r.colIndex, a = r.rowIndex;
				i >= h && i <= g && a >= _ && a <= v && n.push(r);
			}
			n.length && y.push(n);
		}
		return y.length ? y : null;
	}
	_drawOuterBorder(e) {
		let { ctx: t, startX: n, startY: r, width: i, height: a, isDrawFullBorder: o, borderExternalWidth: s } = e, { scale: c } = this.options, l = t.lineWidth;
		s && (t.lineWidth = s * c), t.beginPath();
		let u = Math.round(n), d = Math.round(r);
		t.translate(.5, .5), o ? t.rect(u, d, i, a) : (t.moveTo(u, d + a), t.lineTo(u, d), t.lineTo(u + i, d)), t.stroke(), s && (t.lineWidth = l), t.translate(-.5, -.5);
	}
	getFragmentTdList(e, t) {
		let n = this.fragmentTdListCache.get(t);
		if (n) return n;
		let { startTrIndex: r, endTrIndex: i, carriedTds: a } = t, o = [...a || []], s = e.trList;
		for (let e = r; e < i; e++) o.push(...s[e].tdList);
		return this.fragmentTdListCache.set(t, o), o;
	}
	_getDrawTdList(e, t) {
		let { scale: n } = this.options, r = e.trList, i = [];
		if (!t) {
			for (let e of r) for (let t of e.tdList) i.push({
				td: t,
				offsetY: 0,
				height: t.height * n,
				isRepeat: !1,
				isCarried: !1
			});
			return i;
		}
		let { startTrIndex: a, repeatTrIndexes: o } = t;
		if (o?.length) {
			let e = 0;
			for (let t of o) {
				let a = r[t];
				for (let t of a.tdList) i.push({
					td: t,
					offsetY: (e - t.y) * n,
					height: t.height * n,
					isRepeat: !0,
					isCarried: !1
				});
				e += a.height;
			}
		}
		for (let r of this.getFragmentTdList(e, t)) {
			let [o, s] = this.getTdWindowInFragment(r, e, t);
			s <= o || i.push({
				td: r,
				offsetY: this.getTdWindowOffsetY(o, t),
				height: (s - o) * n,
				isRepeat: !1,
				isCarried: r.rowIndex < a
			});
		}
		return i;
	}
	_drawSlash(e, t, n, r) {
		let { scale: i } = this.options, { td: a, offsetY: o, height: s } = t;
		e.save();
		let c = a.width * i, l = Math.round(a.x * i + n), u = Math.round(a.y * i + r + o);
		a.slashTypes?.includes(jt.FORWARD) && (e.moveTo(l + c, u), e.lineTo(l, u + s)), a.slashTypes?.includes(jt.BACK) && (e.moveTo(l, u), e.lineTo(l + c, u + s)), e.stroke(), e.restore();
	}
	_drawBorder(e, t, n, r, i, a) {
		let { colgroup: o, trList: s, borderType: c, borderColor: l, borderWidth: u = 1, borderExternalWidth: d } = t;
		if (!o || !s) return;
		let { scale: f, table: { defaultBorderColor: p } } = this.options, m = t.width * f, h = a ? (a.repeatHeight + this.getFragmentContentHeight(t, a)) * f : t.height * f, g = c === kt.EMPTY, _ = c === kt.EXTERNAL, v = c === kt.INTERNAL;
		e.save(), c === kt.DASH && e.setLineDash([3, 3]), e.lineWidth = u * f, e.strokeStyle = l || p, !g && !v && this._drawOuterBorder({
			ctx: e,
			startX: n,
			startY: r,
			width: m,
			height: h,
			borderExternalWidth: d,
			isDrawFullBorder: _
		});
		for (let t of i) {
			let { td: i, offsetY: c, height: l } = t;
			if (i.slashTypes?.length && this._drawSlash(e, t, n, r), !i.borderTypes?.length && (g || _)) continue;
			let p = i.width * f, m = Math.round(i.x * f + n + p), h = Math.round(i.y * f + r + c);
			if (e.translate(.5, .5), e.beginPath(), i.borderTypes?.includes(At.TOP) && (e.moveTo(m - p, h), e.lineTo(m, h), e.stroke()), i.borderTypes?.includes(At.RIGHT) && (e.moveTo(m, h), e.lineTo(m, h + l), e.stroke()), i.borderTypes?.includes(At.BOTTOM) && (e.moveTo(m, h + l), e.lineTo(m - p, h + l), e.stroke()), i.borderTypes?.includes(At.LEFT) && (e.moveTo(m - p, h), e.lineTo(m - p, h + l), e.stroke()), !g && !_) {
				if ((!v || i.colIndex + i.colspan < o.length) && (e.moveTo(m, h), e.lineTo(m, h + l), d && d !== u && i.colIndex + i.colspan === o.length)) {
					let t = e.lineWidth;
					e.lineWidth = d * f, e.stroke(), e.beginPath(), e.lineWidth = t;
				}
				if (!v || i.rowIndex + i.rowspan < s.length) {
					let t = i.rowIndex + i.rowspan === (a?.endTrIndex ?? s.length), n = d && d !== u && t;
					if (n && (e.stroke(), e.beginPath()), e.moveTo(m, h + l), e.lineTo(m - p, h + l), n) {
						let t = e.lineWidth;
						e.lineWidth = d * f, e.stroke(), e.beginPath(), e.lineWidth = t;
					}
				}
				e.stroke();
			}
			e.translate(-.5, -.5);
		}
		e.restore();
	}
	_drawBackgroundColor(e, t, n, r) {
		let { scale: i } = this.options;
		for (let { td: a, offsetY: o, height: s } of r) {
			if (!a.backgroundColor) continue;
			e.save();
			let r = a.width * i, c = Math.round(a.x * i + t), l = Math.round(a.y * i + n + o);
			e.fillStyle = a.backgroundColor, e.fillRect(c, l, r, s), e.restore();
		}
	}
	getTableWidth(e) {
		return e.colgroup.reduce((e, t) => e + t.width, 0);
	}
	getFragmentTrHeight(e, t, n) {
		if (!n) return e.height;
		let r = e.height;
		return t === n.startTrIndex && n.startSplitTrOffset && (r -= n.startSplitTrOffset), t === n.endTrIndex - 1 && n.endSplitTrHeight !== void 0 && (r -= Math.max(0, e.height - n.endSplitTrHeight)), r;
	}
	getFragmentContentHeight(e, t) {
		let n = this.fragmentContentHeightCache.get(t);
		if (n !== void 0) return n;
		let { startTrIndex: r, endTrIndex: i, startSplitTrOffset: a, endSplitTrHeight: o } = t, s = e.trList, c = 0;
		for (let e = r; e < i; e++) {
			let t = s[e].height;
			e === r && a && (t -= a), e === i - 1 && o !== void 0 && (t -= Math.max(0, s[e].height - o)), c += t;
		}
		return this.fragmentContentHeightCache.set(t, c), c;
	}
	getTdWindowInFragment(e, t, n) {
		let { skipHeight: r, startSplitTrOffset: i } = n, a = r + (i ?? 0), o = a + this.getFragmentContentHeight(t, n);
		return [Math.max(0, a - e.y), Math.min(e.height, o - e.y)];
	}
	getTdWindowOffsetY(e, t) {
		let { scale: n } = this.options;
		return (e - t.skipHeight - (t.startSplitTrOffset ?? 0) + t.repeatHeight) * n;
	}
	getTdVisibleRowListByWindow(e, t, n) {
		let r = e.rowList, [i, a] = this.getTdLineRangeBySplitWindow(e, t, n);
		return {
			rowList: r.slice(i, a),
			startIndex: r[i]?.startIndex ?? 0,
			startRowIndex: i
		};
	}
	getTdLineRangeBySplitWindow(e, t, n) {
		let { scale: r } = this.options, i = e.rowList || [], a = this.tdLineHeightPrefixCache.get(i);
		if (!a) {
			let { table: { tdPadding: e } } = this.options;
			a = [e[0] * r];
			for (let e = 0; e < i.length; e++) a.push(a[e] + i[e].height);
			this.tdLineHeightPrefixCache.set(i, a);
		}
		let o = t * r, s = n * r, c = (e) => {
			let t = 0, n = i.length;
			for (; t < n;) {
				let r = t + n + 1 >> 1;
				a[r] <= e ? t = r : n = r - 1;
			}
			return t;
		};
		return [c(o), c(s)];
	}
	getTableHeight(e) {
		let t = e.trList;
		return t?.length ? this.getTdListByColIndex(t, 0).reduce((e, t) => e + t.height, 0) : 0;
	}
	getRowCountByColIndex(e, t) {
		return this.getTdListByColIndex(e, t).reduce((e, t) => e + t.rowspan, 0);
	}
	getTdListByColIndex(e, t) {
		let n = [];
		for (let r = 0; r < e.length; r++) {
			let i = e[r].tdList;
			for (let e = 0; e < i.length; e++) {
				let r = i[e], a = r.colIndex, o = a + r.colspan - 1;
				t >= a && t <= o && n.push(r);
			}
		}
		return n;
	}
	getTdListByRowIndex(e, t) {
		let n = [];
		for (let r = 0; r < e.length; r++) {
			let i = e[r].tdList;
			for (let e = 0; e < i.length; e++) {
				let r = i[e], a = r.rowIndex, o = a + r.rowspan - 1;
				t >= a && t <= o && n.push(r);
			}
		}
		return n;
	}
	computeRowColInfo(e) {
		let { colgroup: t, trList: n } = e;
		if (!t || !n) return;
		let r = 0;
		for (let e = 0; e < n.length; e++) {
			let i = n[e], a = n.length - 1 === e, o = 0;
			for (let s = 0; s < i.tdList.length; s++) {
				let c = i.tdList[s], l = 0;
				if (n.length > 1 && e !== 0) {
					let a = i.tdList[s - 1], o = a ? a.colIndex + a.colspan : s;
					for (let i = o; i < t.length; i++) if (this.getRowCountByColIndex(n.slice(0, e), i) === e) {
						l = i;
						let e = 0;
						for (let n = 0; n < i; n++) e += t[n].width;
						r = e;
						break;
					}
				} else {
					let e = i.tdList[s - 1];
					e && (l = e.colIndex + e.colspan);
				}
				let u = 0;
				for (let e = 0; e < c.colspan; e++) u += t[e + l].width;
				let d = 0;
				for (let t = 0; t < c.rowspan; t++) {
					let r = n[t + e] || n[e];
					d += r.height;
				}
				(o === 0 || o > d) && (o = d);
				let f = i.tdList.length - 1 === s, p = a;
				if (!p && c.rowspan > 1) {
					let t = n.length - 1 - e;
					p = c.rowspan - 1 === t;
				}
				let m = a && f;
				c.isLastRowTd = f, c.isLastColTd = p, c.isLastTd = m, c.x = r;
				let h = 0;
				for (let t = 0; t < e; t++) {
					let e = n[t].tdList;
					for (let t = 0; t < e.length; t++) {
						let n = e[t];
						if (l >= n.colIndex && l < n.colIndex + n.colspan) {
							h += n.height;
							break;
						}
					}
				}
				c.y = h, c.width = u, c.height = d, c.rowIndex = e, c.colIndex = l, c.trIndex = e, c.tdIndex = s, r += u, f && !m && (r = 0);
			}
		}
	}
	drawRange(e, t, n, r, i) {
		let { scale: a, rangeAlpha: o, rangeColor: s } = this.options, { type: c, trList: l } = t;
		if (!l || c !== H.TABLE) return;
		let { isCrossRowCol: u, tableId: d, startTdIndex: f, endTdIndex: p, startTrIndex: m, endTrIndex: h } = this.range.getRange();
		if (!u || d !== t.id) return;
		let g = l[m].tdList[f], _ = l[h].tdList[p];
		(g.x > _.x || g.y > _.y) && ([g, _] = [_, g]);
		let v = g.colIndex, y = _.colIndex + (_.colspan - 1), b = g.rowIndex, x = _.rowIndex + (_.rowspan - 1);
		e.save();
		let S = this._getDrawTdList(t, i);
		for (let { td: t, offsetY: i, height: c, isRepeat: l } of S) {
			if (l) continue;
			let u = t.colIndex, d = t.rowIndex;
			if (u >= v && u <= y && d >= b && d <= x) {
				let l = t.x * a, u = t.y * a + i, d = t.width * a;
				e.globalAlpha = o, e.fillStyle = s, e.fillRect(l + n, u + r, d, c);
			}
		}
		e.restore();
	}
	render(e, t, n, r, i) {
		let a = this._getDrawTdList(t, i);
		this._drawBackgroundColor(e, n, r, a), this._drawBorder(e, t, n, r, a, i);
	}
}, gi = class {
	draw;
	options;
	tableParticle;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.tableParticle = e.getTableParticle();
	}
	splitTableRowAcrossPages(e) {
		let { scale: t } = this.options, n = this.draw.getColumnLayout(this.options.paperDirection)?.count || 1, r = n > 1, i = this.options.paperDirection, a = this.draw.getHeight(i), o = 0, s = 0, c = this.draw.getMainOuterHeight(0, i), l = [], u = !1;
		for (let d = 0; d < e.length; d++) {
			let f = e[d], p = f.elementList[0], m = p?.trList, h = !!e[d - 1]?.isPageBreak, g = h ? e[d - 1].paperDirection || this.options.paperDirection : null, _ = () => {
				r && s < n - 1 ? s++ : (o++, s = 0), c = this.draw.getMainOuterHeight(o, i);
			}, v = () => {
				r && f.columnIndex !== void 0 && f.columnIndex > s && !u && (s = f.columnIndex, c = this.draw.getMainOuterHeight(o, i)), (f.height + (f.offsetY || 0) + c > a || h) && (g && (i = g, a = this.draw.getHeight(i)), _()), r && (f.columnIndex = s), c += f.height + (f.offsetY || 0), l.push(f);
			}, y = p?.type === H.TABLE && (p.hide || p.control?.hide || p.area?.hide && !this.draw.isAreaHideDisabled() || this.draw.getTraceParticle().isTraceHidden(p)) && !this.draw.isDesignMode();
			if (!(f.elementList.length === 1 && p?.type === H.TABLE && m?.length && !y)) {
				v();
				continue;
			}
			let b = this.draw.getElementRowMargin(p), x = b * 2, S = [0];
			for (let e = 0; e < m.length; e++) S.push(S[e] + m[e].height);
			let C = [];
			for (let e of m) for (let t of e.tdList) t.rowspan > 1 && C.push(t);
			let w = (e) => m[e].tdList.every((e) => !!e.rowList?.length), T = (e) => {
				let t = [...m[e].tdList];
				for (let n of C) n.rowIndex < e && n.rowIndex + n.rowspan > e && t.push(n);
				return t;
			}, { table: { tdPadding: E }, defaultSize: D } = this.options, O = E[0] + E[2] + D, k = (e, n, r) => {
				let i = S[e], a = 0, o = !1, s = 0;
				for (let c of T(e)) {
					let e = Math.min(c.height, i + n - c.y), l = Math.max(0, r - c.y);
					if (e <= l) continue;
					let [u, d] = this.tableParticle.getTdLineRangeBySplitWindow(c, l, e);
					a = Math.max(a, d - u), d < c.rowList.length && (o = !0);
					let f = c.rowList.slice(0, d).reduce((e, t) => e + t.height, 0), p = c.y + E[0] + E[2] + f / t - i;
					s = Math.max(s, p);
				}
				return {
					fit: a,
					hasRemaining: o,
					consumedHeight: s
				};
			}, A = o, j = s, M = c;
			r && f.columnIndex !== void 0 && f.columnIndex > s && (j = f.columnIndex, M = this.draw.getMainOuterHeight(A, i));
			let N = () => {
				r && j < n - 1 ? j++ : (A++, j = 0), M = this.draw.getMainOuterHeight(A, i);
			};
			if (h) g && (i = g, a = this.draw.getHeight(i)), N();
			else if (M + m[0].height * t + x > a) {
				let e = a - M - x, { fit: n, hasRemaining: r, consumedHeight: i } = w(0) ? k(0, e / t, 0) : {
					fit: 0,
					hasRemaining: !1,
					consumedHeight: 0
				}, o = -1;
				n >= 1 && (r ? (o = Math.min(i, e / t), m[0].height - o < O && (o = m[0].height - O)) : m[0].height - e / t >= O && (o = e / t)), o <= 0 && N();
			}
			let ee = p.height * t;
			if (M + x + ee <= a) {
				v();
				continue;
			}
			let P = [], F = 0, I = 0, te = A, L = j, ne = M, re = [], R = 0, z = !1;
			for (; F < m.length;) {
				let e = P.length === 0;
				if (!e && (r && L < n - 1 ? L++ : (te++, L = 0), ne = this.draw.getMainOuterHeight(te, i), P.length === 1)) {
					for (let e = 0; e < P[0].endTrIndex; e++) {
						let t = m[e];
						t.pagingRepeat && (re.push(e), R += t.height);
					}
					re.length && a - ne - x - R * t < O * t && (re.length = 0, R = 0);
				}
				let o = x + (e ? 0 : R * t), s = a - ne - o;
				if (s < O * t) {
					z = !0;
					break;
				}
				let c = S[F] + I;
				if (I > 0 && (m[F].height - I) * t > s) {
					let e = I + s / t, { fit: n, hasRemaining: r, consumedHeight: i } = k(F, e, c), a = e;
					n >= 1 && r && (a = Math.min(i, e), m[F].height - a < O && (a = Math.max(I + 1, m[F].height - O))), a <= I && (a = I + 1), P.push({
						startTrIndex: F,
						endTrIndex: F + 1,
						startSplitTrOffset: I,
						endSplitTrHeight: a,
						columnIndex: L
					}), I = a;
					continue;
				}
				let l = I > 0 ? (m[F].height - I) * t : 0, u = I > 0 ? F + 1 : F, d, f = !1, p = !1;
				for (;;) {
					if (u >= m.length) {
						p = !0;
						break;
					}
					let e = m[u].height * t;
					if (l + e <= s) {
						l += e, u++;
						continue;
					}
					let n = s - l;
					if (w(u)) {
						let { fit: e, hasRemaining: r, consumedHeight: i } = k(u, n / t, c), a = -1;
						if (e >= 1 && (r ? (a = Math.min(i, n / t), m[u].height - a < O && (a = m[u].height - O)) : m[u].height - n / t >= O && (a = n / t)), a > 0) {
							d = a;
							break;
						}
					}
					u <= F && (P.length ? (u = m.length, p = !0) : f = !0);
					break;
				}
				if (f) {
					z = !0;
					break;
				}
				if (P.push({
					startTrIndex: F,
					endTrIndex: d === void 0 ? u : u + 1,
					startSplitTrOffset: I || void 0,
					endSplitTrHeight: d,
					columnIndex: L
				}), F = u, I = d ?? 0, p) break;
			}
			if (z) {
				v();
				continue;
			}
			u = !0;
			let B = f.elementList[0], ie = 0, V = 0;
			for (let e = 0; e < P.length; e++) {
				let n = P[e], i = e === 0, a = !i && re.length ? re : void 0, o = a ? R : 0, s = (this.tableParticle.getFragmentContentHeight(p, n) + o) * t;
				l.push({
					...f,
					height: s + b,
					offsetY: i ? f.offsetY : 0,
					isList: i ? f.isList : !1,
					...r ? { columnIndex: n.columnIndex } : {},
					elementList: [{
						...B,
						metrics: {
							width: B.metrics.width,
							height: s,
							boundingBoxAscent: B.metrics.boundingBoxAscent,
							boundingBoxDescent: s
						}
					}],
					tableFragment: {
						startTrIndex: n.startTrIndex,
						endTrIndex: n.endTrIndex,
						skipHeight: ie,
						repeatHeight: o,
						repeatTrIndexes: a,
						startSplitTrOffset: n.startSplitTrOffset,
						endSplitTrHeight: n.endSplitTrHeight,
						carriedTds: C.length ? C.filter((e) => e.rowIndex < n.startTrIndex && e.rowIndex + e.rowspan > n.startTrIndex) : void 0
					}
				});
				let c = P[e + 1]?.startTrIndex ?? 0;
				for (; V < c;) ie += m[V].height, V++;
			}
			o = te, s = L;
			let ae = l[l.length - 1];
			c = this.draw.getMainOuterHeight(o, i) + ae.height + (ae.offsetY || 0);
		}
		for (let e = 0; e < l.length; e++) l[e].rowIndex = e;
		return l;
	}
	truncateTableByFragment(e, t, n) {
		let { startTrIndex: r, startSplitTrOffset: i, skipHeight: a } = t, o = e.trList, s = /* @__PURE__ */ new Set(), c = r;
		if (i) {
			let e = o[r];
			for (let t of e.tdList) this._trimTdContentToWindow(t, i) && s.add(t), t.height = i;
			e.height = i, e.minHeight = Math.min(e.minHeight ?? i, i);
			let t = a + i;
			for (let e = 0; e < r; e++) for (let n of o[e].tdList) {
				if (n.rowIndex + n.rowspan <= r) continue;
				let e = t - n.y;
				e >= n.height || this._trimTdContentToWindow(n, e) && s.add(n);
			}
			c = r + 1;
		}
		if (!c) return !1;
		let l = [0];
		for (let e = 0; e < c; e++) l.push(l[e] + o[e].height);
		for (let e = 0; e < c; e++) for (let t of o[e].tdList) t.rowIndex + t.rowspan > c && (t.rowspan = c - t.rowIndex), t.height = l[t.rowIndex + t.rowspan] - l[t.rowIndex];
		return e.trList = o.slice(0, c), e.height = this.tableParticle.getTableHeight(e), this._repairTableContextAfterTruncate(e, c, s, n), !0;
	}
	_trimTdContentToWindow(e, t) {
		let n = e.value.length, { scale: r, table: { tdPadding: i } } = this.options, [, a] = this.tableParticle.getTdLineRangeBySplitWindow(e, 0, Math.max(0, t)), o = e.rowList, s = i[0] + i[2], c = 0, l = 0;
		for (let e = 0; e < a; e++) {
			let n = c + o[e].height / r;
			if (s + n > t) break;
			c = n, l = e + 1;
		}
		a = l;
		let u = a < o.length ? o[a].startIndex : e.value.length;
		if (!u) {
			let { trId: t, tableId: n } = e.value[0] || {};
			return e.value = [{
				value: "​",
				tdId: e.id,
				trId: t,
				tableId: n
			}], e.rowList = this.draw.computeRowList({
				innerWidth: (e.width - (i[1] + i[3])) * r,
				elementList: e.value,
				isFromTable: !0,
				isPagingMode: this.draw.getIsPagingMode()
			}), !0;
		}
		return e.value = e.value.slice(0, u), e.rowList = o.slice(0, a), u < n;
	}
	_repairTableContextAfterTruncate(e, t, n, r) {
		let i = this.draw.getRange().getRange();
		if (i.isCrossRowCol && i.tableId === e.id && ((i.startTrIndex ?? 0) >= t || (i.endTrIndex ?? 0) >= t)) {
			let e = this.draw.getPosition().getTableTdByContext(r, this.draw.getPosition().getPositionContext()), t = Math.max(0, (e?.value.length ?? 1) - 1);
			this.draw.getRange().setRange(t, t);
		}
		let a = this.draw.getPosition().getPositionContext();
		if (!a.isTable) return;
		let o = a.tablePath?.[0], s = o ? o.index : a.index, c = o ? o.trIndex : a.trIndex;
		if (s === void 0 || r[s] !== e) return;
		let l = o?.trIndex ?? a.trIndex, u = o?.tdIndex ?? a.tdIndex, d = l !== void 0 && u !== void 0 ? e.trList?.[l]?.tdList[u] : void 0;
		if (d && n.has(d) && this.draw.getPosition().setPositionContext({
			isTable: !0,
			index: a.index,
			trIndex: a.trIndex,
			tdIndex: a.tdIndex,
			tdId: a.tdId,
			trId: a.trId,
			tableId: a.tableId,
			tablePath: a.tablePath
		}), c !== void 0 && c >= t) {
			let n = this.tableParticle.getTdListByRowIndex(e.trList, t - 1), r = n[n.length - 1];
			if (r) {
				let t = {
					isTable: !0,
					index: s,
					tablePath: o ? [o] : void 0
				};
				this.draw.getPosition().setPositionContext(this.draw.getPosition().buildTablePositionContext(t, e, r.rowIndex, r.tdIndex)), this.draw.getRange().setRange(Math.max(0, r.value.length - 1), Math.max(0, r.value.length - 1));
			} else this.draw.getPosition().setPositionContext({ isTable: !1 });
		} else if (o && !this.draw.getPosition().getTableTdByContext(r, a)) {
			let t = {
				isTable: !0,
				index: s,
				tablePath: [o]
			};
			this.draw.getPosition().setPositionContext(this.draw.getPosition().buildTablePositionContext(t, e, o.trIndex, o.tdIndex));
		}
		let f = this.draw.getPosition().getTableTdByContext(r, this.draw.getPosition().getPositionContext());
		if (f) {
			let e = f.value.length - 1, { startIndex: t, endIndex: n, isCrossRowCol: r } = this.draw.getRange().getRange();
			!r && e >= 0 && (t > e || n > e) && this.draw.getRange().setRange(Math.min(t, e), Math.min(n, e));
		}
	}
}, _i;
(function(e) {
	e.ROW = "row", e.COL = "col";
})(_i ||= {});
//#endregion
//#region src/editor/core/draw/particle/table/TableTool.ts
var vi = class {
	MIN_TD_WIDTH = 20;
	ROW_COL_OFFSET = 18;
	ROW_COL_QUICK_WIDTH = 16;
	ROW_COL_QUICK_OFFSET = 5;
	ROW_COL_QUICK_POSITION = this.ROW_COL_OFFSET + (this.ROW_COL_OFFSET - this.ROW_COL_QUICK_WIDTH) / 2;
	BORDER_VALUE = 4;
	TABLE_SELECT_OFFSET = 20;
	draw;
	canvas;
	options;
	position;
	range;
	container;
	toolRowContainer;
	toolRowAddBtn;
	toolColAddBtn;
	toolTableSelectBtn;
	toolColContainer;
	toolBorderContainer;
	anchorLine;
	mousedownX;
	mousedownY;
	lastAnchorKey;
	anchorPageNo;
	constructor(e) {
		this.draw = e, this.canvas = e.getPage(), this.options = e.getOptions(), this.position = e.getPosition(), this.range = e.getRange(), this.container = e.getContainer(), this.toolRowContainer = null, this.toolRowAddBtn = null, this.toolColAddBtn = null, this.toolTableSelectBtn = null, this.toolColContainer = null, this.toolBorderContainer = null, this.anchorLine = null, this.mousedownX = 0, this.mousedownY = 0, this.lastAnchorKey = null, this.anchorPageNo = 0;
	}
	dispose() {
		this.toolRowContainer?.remove(), this.toolRowAddBtn?.remove(), this.toolColAddBtn?.remove(), this.toolTableSelectBtn?.remove(), this.toolColContainer?.remove(), this.toolBorderContainer?.remove(), this.toolRowContainer = null, this.toolRowAddBtn = null, this.toolColAddBtn = null, this.toolTableSelectBtn = null, this.toolColContainer = null, this.toolBorderContainer = null, this.lastAnchorKey = null;
	}
	render() {
		let e = this.position.getPositionContext(), { isTable: t } = e;
		if (!t) return;
		let n = this.draw.getOriginalElementList(), r = this.position.getOriginalPositionList(), i = this.position.getTableElementByContext(n, e), a = this.position.getTableElementPositionByContext(n, r, e);
		if (!i || !a) {
			this.dispose();
			return;
		}
		if (i.tableToolDisabled && !this.draw.isDesignMode()) {
			this.dispose();
			return;
		}
		let { scale: o, table: { overflow: s } } = this.options, { colgroup: c, trList: l } = i, { coordinate: { leftTop: u } } = a, d = a.tableFragment, f = d?.startTrIndex ?? 0, p = d?.endTrIndex ?? l.length, m = `${o}:${u[0]}:${u[1]}:${a.metrics.height}:${f}:${p}:${d?.startSplitTrOffset ?? 0}:${d?.endSplitTrHeight ?? 0}`;
		for (let e = f; e < p; e++) m += `:${l[e].height}`;
		for (let e of c || []) m += `:${e.width}`;
		let h = `${i.id}:${a.pageNo}:${e.trIndex}:${e.tdIndex}:${m}`;
		if (h === this.lastAnchorKey) return;
		this.dispose(), this.anchorPageNo = a.pageNo;
		let { x: g, y: _ } = this.draw.getPageOffset(a.pageNo), v = _, y = u[0] + g, b = u[1] + v, x = this.draw.getTd();
		if (!x) return;
		this.lastAnchorKey = h;
		let S = x.rowIndex, C = x.colIndex, w = a.metrics.height, T = i.width * o, E = document.createElement("div");
		E.classList.add("ce-table-tool__select"), E.style.left = `${y}px`, E.style.top = `${b}px`, E.style.transform = `translate(-${this.TABLE_SELECT_OFFSET * o}px, ${-this.TABLE_SELECT_OFFSET * o}px)`, E.onclick = () => {
			this.draw.getTableOperate().tableSelectAll();
		}, this.container.append(E), this.toolTableSelectBtn = E;
		let D = document.createElement("div");
		D.classList.add("ce-table-tool__row"), D.style.transform = `translateX(-${this.ROW_COL_OFFSET * o}px)`;
		for (let t = f; t < p; t++) {
			let n = this.draw.getTableParticle().getFragmentTrHeight(l[t], t, d) * o, r = document.createElement("div");
			r.classList.add("ce-table-tool__row__item"), t === S && r.classList.add("active"), r.onclick = () => {
				let n = this.draw.getTableParticle().getTdListByRowIndex(l, t), r = n[0], a = n[n.length - 1];
				this.position.setPositionContext(this.position.buildTablePositionContext(e, i, r.trIndex, r.tdIndex)), this.range.setRange(0, 0, i.id, r.tdIndex, a.tdIndex, r.trIndex, a.trIndex), this.draw.render({
					curIndex: 0,
					isCompute: !1,
					isSubmitHistory: !1
				}), this._setAnchorActive(D, t - f);
			};
			let a = document.createElement("div");
			a.classList.add("ce-table-tool__anchor"), a.onmousedown = (e) => {
				this._mousedown({
					evt: e,
					element: i,
					index: t,
					order: _i.ROW
				});
			}, r.append(a), r.style.height = `${n}px`, D.append(r);
		}
		D.style.left = `${y}px`, D.style.top = `${b + (d?.repeatHeight || 0) * o}px`, this.container.append(D), this.toolRowContainer = D;
		let O = document.createElement("div");
		O.classList.add("ce-table-tool__quick__add"), O.style.left = `${y}px`, O.style.top = `${b + w}px`, O.style.transform = `translate(-${this.ROW_COL_QUICK_POSITION * o}px, ${this.ROW_COL_QUICK_OFFSET * o}px)`, O.onclick = () => {
			this.position.setPositionContext(this.position.buildTablePositionContext(e, i, l.length - 1, 0)), this.draw.getTableOperate().insertTableBottomRow();
		}, this.container.append(O), this.toolRowAddBtn = O;
		let k = c.map((e) => e.width), A = document.createElement("div");
		A.classList.add("ce-table-tool__col"), A.style.transform = `translateY(-${this.ROW_COL_OFFSET * o}px)`;
		for (let t = 0; t < k.length; t++) {
			let n = k[t] * o, r = document.createElement("div");
			r.classList.add("ce-table-tool__col__item"), t === C && r.classList.add("active"), r.onclick = () => {
				let n = this.draw.getTableParticle().getTdListByColIndex(l, t), r = n[0], a = n[n.length - 1];
				this.position.setPositionContext(this.position.buildTablePositionContext(e, i, r.trIndex, r.tdIndex)), this.range.setRange(0, 0, i.id, r.tdIndex, a.tdIndex, r.trIndex, a.trIndex), this.draw.render({
					curIndex: 0,
					isCompute: !1,
					isSubmitHistory: !1
				}), this._setAnchorActive(A, t);
			};
			let a = document.createElement("div");
			a.classList.add("ce-table-tool__anchor"), a.onmousedown = (e) => {
				this._mousedown({
					evt: e,
					element: i,
					index: t,
					order: _i.COL
				});
			}, r.append(a), r.style.width = `${n}px`, A.append(r);
		}
		A.style.left = `${y}px`, A.style.top = `${b}px`, this.container.append(A), this.toolColContainer = A;
		let j = document.createElement("div");
		j.classList.add("ce-table-tool__quick__add"), j.style.left = `${y + T}px`, j.style.top = `${b}px`, j.style.transform = `translate(${this.ROW_COL_QUICK_OFFSET * o}px, -${this.ROW_COL_QUICK_POSITION * o}px)`, j.onclick = () => {
			this.position.setPositionContext(this.position.buildTablePositionContext(e, i, 0, l[0].tdList.length - 1 || 0)), this.draw.getTableOperate().insertTableRightCol();
		}, this.container.append(j), this.toolColAddBtn = j;
		let M = document.createElement("div");
		M.classList.add("ce-table-tool__border"), M.style.height = `${w}px`, M.style.width = `${T}px`, M.style.left = `${y}px`, M.style.top = `${b}px`;
		let N = d ? this.draw.getTableParticle().getFragmentTdList(i, d) : l.flatMap((e) => e.tdList);
		for (let e of N) {
			let t = e.height, n = 0;
			if (d) {
				let [r, a] = this.draw.getTableParticle().getTdWindowInFragment(e, i, d);
				t = a - r, n = this.draw.getTableParticle().getTdWindowOffsetY(r, d);
			}
			let r = document.createElement("div");
			r.classList.add("ce-table-tool__border__row"), r.style.width = `${e.width * o}px`, r.style.height = `${this.BORDER_VALUE}px`, r.style.top = `${(e.y + t) * o + n - this.BORDER_VALUE / 2}px`, r.style.left = `${e.x * o}px`, r.onmousedown = (t) => {
				this._mousedown({
					evt: t,
					element: i,
					index: e.rowIndex + e.rowspan - 1,
					order: _i.ROW
				});
			}, M.appendChild(r);
			let a = document.createElement("div");
			if (a.classList.add("ce-table-tool__border__col"), a.style.width = `${this.BORDER_VALUE}px`, a.style.height = `${t * o}px`, a.style.top = `${e.y * o + n}px`, a.style.left = `${(e.x + e.width) * o - this.BORDER_VALUE / 2}px`, a.onmousedown = (t) => {
				this._mousedown({
					evt: t,
					element: i,
					index: e.colIndex + e.colspan - 1,
					order: _i.COL
				});
			}, M.appendChild(a), s && e.colIndex === 0) {
				let r = document.createElement("div");
				r.classList.add("ce-table-tool__border__col"), r.style.width = `${this.BORDER_VALUE}px`, r.style.height = `${t * o}px`, r.style.top = `${e.y * o + n}px`, r.style.left = `${e.x * o - this.BORDER_VALUE / 2}px`, r.onmousedown = (e) => {
					this._mousedown({
						evt: e,
						element: i,
						index: 0,
						isLeftStartBorder: !0,
						order: _i.COL
					});
				}, M.appendChild(r);
			}
		}
		this.container.append(M), this.toolBorderContainer = M;
	}
	_setAnchorActive(e, t) {
		let n = e.children;
		for (let e = 0; e < n.length; e++) {
			let r = n[e];
			e === t ? r.classList.add("active") : r.classList.remove("active");
		}
	}
	_mousedown(e) {
		let { evt: t, index: n, order: r, element: i, isLeftStartBorder: a } = e;
		this.canvas = this.draw.getPage();
		let { scale: o, table: { overflow: s } } = this.options, { width: c, height: l } = this.draw.getPageSize(this.anchorPageNo), { x: u, y: d } = this.draw.getPageOffset(this.anchorPageNo);
		this.mousedownX = t.x, this.mousedownY = t.y;
		let f = t.target, p = this.canvas.getBoundingClientRect(), m = window.getComputedStyle(f).cursor;
		document.body.style.cursor = m, this.canvas.style.cursor = m;
		let h = 0, g = 0, _ = document.createElement("div");
		_.classList.add("ce-table-anchor__line"), r === _i.ROW ? (_.classList.add("ce-table-anchor__line__row"), _.style.width = `${c}px`, h = u, g = d + this.mousedownY - p.top) : (_.classList.add("ce-table-anchor__line__col"), _.style.height = `${l}px`, h = this.mousedownX - p.left, g = d), _.style.left = `${h}px`, _.style.top = `${g}px`, this.container.append(_), this.anchorLine = _;
		let v = 0, y = 0, b = (e) => {
			let t = this._mousemove(e, r, h, g);
			t && (v = t.dx, y = t.dy);
		};
		document.addEventListener("mousemove", b), document.addEventListener("mouseup", () => {
			let e = !1;
			if (r === _i.ROW) {
				let t = i.trList, r = t[n] || t[n - 1], { defaultTrMinHeight: a } = this.options.table;
				y < 0 && r.height + y < a && (y = a - r.height), y && (r.height += y, r.minHeight = r.height, e = !0);
			} else {
				let { colgroup: t } = i;
				if (t && v) {
					if (s && a) t[n].width - v / o <= this.MIN_TD_WIDTH && (v = (t[n].width - this.MIN_TD_WIDTH) * o), t[n].width -= v / o, i.width -= v / o, i.translateX = (i.translateX || 0) + v / o, e = !0;
					else {
						let r = this.draw.getInnerWidth(), a = t[n].width;
						v < 0 && a + v < this.MIN_TD_WIDTH && (v = this.MIN_TD_WIDTH - a);
						let c = t[n + 1]?.width;
						v > 0 && c && c - v < this.MIN_TD_WIDTH && (v = c - this.MIN_TD_WIDTH);
						let l = a + v;
						if (!s && n === t.length - 1) {
							let e = 0;
							for (let r = 0; r < t.length; r++) {
								let i = t[r];
								r === n + 1 && (e -= v), r === n && (e += l), r !== n && (e += i.width);
							}
							e > r && (v = r - i.width);
						}
						v && (t.length - 1 !== n && (t[n + 1].width -= v / o), t[n].width += v / o, e = !0);
					}
				}
			}
			e && this.draw.render({ isSetCursor: !1 }), _.remove(), document.removeEventListener("mousemove", b), document.body.style.cursor = "", this.canvas.style.cursor = "text";
		}, { once: !0 }), t.preventDefault();
	}
	_mousemove(e, t, n, r) {
		if (!this.anchorLine) return null;
		let i = e.x - this.mousedownX, a = e.y - this.mousedownY;
		return t === _i.ROW ? this.anchorLine.style.top = `${r + a}px` : this.anchorLine.style.left = `${n + i}px`, e.preventDefault(), {
			dx: i,
			dy: a
		};
	}
}, yi;
(function(e) {
	e.LEFT = "left", e.RIGHT = "right", e.TOP = "top", e.BOTTOM = "bottom";
})(yi ||= {});
var bi = class {
	MM_PX = 96 / 25.4;
	HANDLE_HIT_TOLERANCE = 7;
	MIN_INNER_SIZE = 100;
	draw;
	options;
	container;
	rulerContainer;
	canvasX;
	ctxX;
	canvasY;
	ctxY;
	dragSide;
	dragStartPosition;
	dragOriginMargins;
	mousemoveHandler;
	mouseupHandler;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer(), this.rulerContainer = null, this.canvasX = null, this.ctxX = null, this.canvasY = null, this.ctxY = null, this.dragSide = null, this.dragStartPosition = 0, this.dragOriginMargins = null, this.mousemoveHandler = this._dragMargin.bind(this), this.mouseupHandler = this._stopDrag.bind(this);
	}
	isEnable() {
		return !this.options.ruler.disabled;
	}
	_createDOM() {
		let e = document.createElement("canvas");
		e.classList.add("ce-ruler-y");
		let t = document.createElement("canvas");
		t.classList.add("ce-ruler-x");
		let n = document.createElement("div");
		n.classList.add("ce-ruler"), n.append(e, t), n.addEventListener("mousedown", (t) => {
			t.preventDefault(), t.stopPropagation(), t.target === e ? this._mousedownY(t) : this._mousedownX(t);
		}), n.addEventListener("mousemove", (t) => {
			t.target === e ? this._updateCursorY(t) : this._updateCursorX(t);
		}), this.container.insertBefore(n, this.draw.getPageContainer()), this.rulerContainer = n, this.canvasX = t, this.ctxX = t.getContext("2d"), this.canvasY = e, this.ctxY = e.getContext("2d");
	}
	setEnabled(e) {
		this.options.ruler.disabled = !e, this.render();
	}
	dispose() {
		this._stopDrag(), this.rulerContainer?.remove(), this.rulerContainer = null, this.canvasX = null, this.ctxX = null, this.canvasY = null, this.ctxY = null;
	}
	render() {
		if (!this.isEnable()) {
			this.rulerContainer && (this.rulerContainer.style.display = "none");
			return;
		}
		this.rulerContainer || this._createDOM();
		let e = this.rulerContainer;
		if (this.options.pageMode !== h.PAGING) {
			e.style.display = "none";
			return;
		}
		e.style.display = "block", this._renderX(), this._renderY();
	}
	_renderX() {
		let e = this.canvasX, t = this.ctxX, { height: n } = this.options.ruler, r = this.draw.getWidth(), i = this.draw.getPagePixelRatio();
		e.style.width = `${r}px`, e.style.height = `${n}px`, e.width = r * i, e.height = n * i, t.scale(i, i), t.clearRect(0, 0, r, n), t.fillStyle = "#ffffff", t.fillRect(0, 0, r, n);
		let a = this.draw.getMargins(), o = this.options.scale;
		t.fillStyle = "#f2f2f2", t.fillRect(0, 0, a[3], n), t.fillRect(r - a[1], 0, a[1], n), t.strokeStyle = "#999999", t.fillStyle = "#666666", t.font = "8px sans-serif", t.textAlign = "center", t.beginPath();
		let s = this.MM_PX * o, c = Math.floor(r / s);
		for (let e = 0; e <= c; e++) {
			let i = Math.round(e * s) + .5, a = e % 10 == 0, o = a ? 10 : e % 5 == 0 ? 7 : 4;
			t.moveTo(i, n), t.lineTo(i, n - o), a && e > 0 && i >= 8 && i <= r - 8 && t.fillText(String(e / 10), i, 9);
		}
		t.stroke(), t.beginPath(), t.strokeStyle = "#e0e0e0", t.moveTo(0, n - .5), t.lineTo(r, n - .5), t.stroke(), this._drawXHandle(t, a[3], n), this._drawXHandle(t, r - a[1], n);
	}
	_renderY() {
		let e = this.canvasY, t = this.ctxY, n = this.options.ruler.height, r = this.draw.getHeight(), i = this.draw.getPagePixelRatio();
		e.style.width = `${n}px`, e.style.height = `${r}px`, e.width = n * i, e.height = r * i, t.scale(i, i), t.clearRect(0, 0, n, r), t.fillStyle = "#ffffff", t.fillRect(0, 0, n, r);
		let a = this.draw.getMargins(), o = this.options.scale;
		t.fillStyle = "#f2f2f2", t.fillRect(0, 0, n, a[0]), t.fillRect(0, r - a[2], n, a[2]), t.strokeStyle = "#999999", t.fillStyle = "#666666", t.font = "8px sans-serif", t.textAlign = "center", t.beginPath();
		let s = this.MM_PX * o, c = Math.floor(r / s);
		for (let e = 0; e <= c; e++) {
			let i = Math.round(e * s) + .5, a = e % 10 == 0, o = a ? 10 : e % 5 == 0 ? 7 : 4;
			t.moveTo(n, i), t.lineTo(n - o, i), a && e > 0 && i >= 8 && i <= r - 8 && (t.save(), t.translate(9, i), t.rotate(-Math.PI / 2), t.fillText(String(e / 10), 0, 0), t.restore());
		}
		t.stroke(), t.beginPath(), t.strokeStyle = "#e0e0e0", t.moveTo(n - .5, 0), t.lineTo(n - .5, r), t.stroke(), this._drawYHandle(t, a[0], n), this._drawYHandle(t, r - a[2], n);
	}
	_drawXHandle(e, t, n) {
		e.beginPath(), e.fillStyle = "#595959", e.moveTo(t - 5, n - 7), e.lineTo(t + 5, n - 7), e.lineTo(t, n), e.closePath(), e.fill();
	}
	_drawYHandle(e, t, n) {
		e.beginPath(), e.fillStyle = "#595959", e.moveTo(n - 7, t - 5), e.lineTo(n - 7, t + 5), e.lineTo(n, t), e.closePath(), e.fill();
	}
	_getHitMarginSideX(e) {
		let t = this.draw.getWidth(), n = this.draw.getMargins();
		return Math.abs(e - n[3]) <= this.HANDLE_HIT_TOLERANCE ? yi.LEFT : Math.abs(e - (t - n[1])) <= this.HANDLE_HIT_TOLERANCE ? yi.RIGHT : null;
	}
	_getHitMarginSideY(e) {
		let t = this.draw.getHeight(), n = this.draw.getMargins();
		return Math.abs(e - n[0]) <= this.HANDLE_HIT_TOLERANCE ? yi.TOP : Math.abs(e - (t - n[2])) <= this.HANDLE_HIT_TOLERANCE ? yi.BOTTOM : null;
	}
	_getRelativeX(e) {
		if (!this.rulerContainer) return 0;
		let t = this.rulerContainer.getBoundingClientRect();
		return e.clientX - t.left;
	}
	_getRelativeY(e) {
		if (!this.canvasY) return 0;
		let t = this.canvasY.getBoundingClientRect();
		return e.clientY - t.top;
	}
	_isMarginDragDisabled() {
		let e = this.draw.getMode();
		return this.draw.isReadonly() || e === p.PRINT || e === p.FORM;
	}
	_startDrag(e, t) {
		this.dragSide = e, this.dragStartPosition = t, this.dragOriginMargins = [...this.draw.getOriginalMargins()], this.draw.getRange().clearRange(), this.draw.getCursor().drawCursor({ isShow: !1 }), document.addEventListener("mousemove", this.mousemoveHandler), document.addEventListener("mouseup", this.mouseupHandler);
	}
	_mousedownX(e) {
		if (this._isMarginDragDisabled()) return;
		let t = this._getHitMarginSideX(this._getRelativeX(e));
		t && this._startDrag(t, e.clientX);
	}
	_mousedownY(e) {
		if (this._isMarginDragDisabled()) return;
		let t = this._getHitMarginSideY(this._getRelativeY(e));
		t && this._startDrag(t, e.clientY);
	}
	_updateCursorX(e) {
		if (!this.canvasX) return;
		let t = this._getHitMarginSideX(this._getRelativeX(e));
		this.canvasX.style.cursor = t ? "col-resize" : "default";
	}
	_updateCursorY(e) {
		if (!this.canvasY) return;
		let t = this._getHitMarginSideY(this._getRelativeY(e));
		this.canvasY.style.cursor = t ? "row-resize" : "default";
	}
	_dragMargin(e) {
		if (!this.dragSide || !this.dragOriginMargins || !this.rulerContainer) return;
		let t = this.options.scale, n = [...this.dragOriginMargins];
		if (this.dragSide === yi.LEFT || this.dragSide === yi.RIGHT) {
			let r = this.draw.getOriginalWidth(), i = (e.clientX - this.dragStartPosition) / t;
			this.dragSide === yi.LEFT ? n[3] = this.clampMargin(n[3] + i, r - n[1] - this.MIN_INNER_SIZE) : n[1] = this.clampMargin(n[1] - i, r - n[3] - this.MIN_INNER_SIZE);
		} else {
			let r = this.draw.getOriginalHeight(), i = (e.clientY - this.dragStartPosition) / t;
			this.dragSide === yi.TOP ? n[0] = this.clampMargin(n[0] + i, r - n[2] - this.MIN_INNER_SIZE) : n[2] = this.clampMargin(n[2] - i, r - n[0] - this.MIN_INNER_SIZE);
		}
		this._setDisplayedMargins(n.map((e) => Math.round(e)));
	}
	_stopDrag() {
		this.dragSide && (this.dragSide = null, this.dragStartPosition = 0, this.dragOriginMargins = null, document.removeEventListener("mousemove", this.mousemoveHandler), document.removeEventListener("mouseup", this.mouseupHandler));
	}
	clampMargin(e, t) {
		return Math.min(Math.max(e, 0), Math.max(t, 0));
	}
	_setDisplayedMargins(e) {
		let { paperDirection: t, margins: n } = this.options, r = t === g.VERTICAL ? e : [
			e[3],
			e[0],
			e[1],
			e[2]
		];
		r.join() !== n.join() && this.draw.setPaperMargin(r);
	}
}, xi = class {
	draw;
	options;
	container;
	hyperlinkPopupContainer;
	hyperlinkDom;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer();
		let { hyperlinkPopupContainer: t, hyperlinkDom: n } = this._createHyperlinkPopupDom();
		this.hyperlinkDom = n, this.hyperlinkPopupContainer = t;
	}
	_createHyperlinkPopupDom() {
		let e = document.createElement("div");
		e.classList.add("ce-hyperlink-popup");
		let t = document.createElement("a");
		return t.target = "_blank", t.rel = "noopener", e.append(t), this.container.append(e), {
			hyperlinkPopupContainer: e,
			hyperlinkDom: t
		};
	}
	drawHyperlinkPopup(e, t) {
		let { coordinate: { leftTop: [n, r] }, lineHeight: i } = t, { x: a, y: o } = this.draw.getPageOffset(this.draw.getPageNo());
		this.hyperlinkPopupContainer.style.display = "block", this.hyperlinkPopupContainer.style.left = `${n + a}px`, this.hyperlinkPopupContainer.style.top = `${r + o + i}px`;
		let s = e.url || "#";
		this.hyperlinkDom.href = s, this.hyperlinkDom.title = s, this.hyperlinkDom.innerText = s;
	}
	clearHyperlinkPopup() {
		this.hyperlinkPopupContainer.style.display = "none";
	}
	openHyperlink(e) {
		let t = window.open(e.url, "_blank");
		t && (t.opener = null);
	}
	render(e, t, n, r) {
		e.save(), e.font = t.style, t.color ||= this.options.defaultHyperlinkColor, e.fillStyle = t.color, t.underline === void 0 && (t.underline = !0), e.fillText(t.value, n, r), e.restore();
	}
}, Si = class {
	draw;
	options;
	container;
	hintPopupContainer;
	hintDom;
	lastHoverKey;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer(), this.lastHoverKey = "";
		let { popup: t, hintDom: n } = this._createHintPopupDom();
		this.hintPopupContainer = t, this.hintDom = n;
	}
	_createHintPopupDom() {
		let e = document.createElement("div");
		e.classList.add("ce-hint-popup");
		let t = document.createElement("span");
		return t.classList.add("ce-hint-popup__text"), e.append(t), this.container.append(e), {
			popup: e,
			hintDom: t
		};
	}
	_getElementHint(e) {
		return e?.hint || "";
	}
	drawHintPopup(e, t) {
		let n = e.position, r = e.td;
		if (!n && !r) {
			this.clearHintPopup();
			return;
		}
		let i, a, o;
		if (n) {
			let { coordinate: { leftTop: [e, t] }, lineHeight: r } = n;
			i = e, a = t, o = r;
		} else i = r.x || 0, a = r.y || 0, o = r.rowList?.[0]?.height || 0;
		let { x: s, y: c } = this.draw.getPageOffset(t), { backgroundColor: l, color: u, fontSize: d, maxWidth: f } = this.options.hint;
		this.hintDom.innerText = e.hint, this.hintPopupContainer.style.background = l, this.hintPopupContainer.style.color = u, this.hintPopupContainer.style.fontSize = `${d}px`, this.hintPopupContainer.style.maxWidth = `${f}px`;
		let p = i + s, m = a + c + o + 6;
		this.hintPopupContainer.style.left = `${p}px`, this.hintPopupContainer.style.top = `${m}px`, this.hintPopupContainer.style.display = "block";
		let h = this.hintPopupContainer.getBoundingClientRect(), { height: g } = h, _ = window.innerWidth, v = window.innerHeight;
		if (h.right > _ && (p = Math.max(0, p - (h.right - _))), h.bottom > v) {
			let e = a + c - g - 6;
			m = e >= 0 ? e : Math.max(0, m - (h.bottom - v));
		}
		this.hintPopupContainer.style.left = `${p}px`, this.hintPopupContainer.style.top = `${m}px`;
	}
	clearHintPopup() {
		this.hintPopupContainer.style.display = "none", this.lastHoverKey = "";
	}
	handleMouseMove(e) {
		if (this.options.hint.disabled) return;
		let t = e.target.dataset.index;
		t && this.draw.setPageNo(Number(t));
		let n = this.draw.getPosition(), r = n.getPositionByXY({
			x: e.offsetX,
			y: e.offsetY
		});
		if (!~r.index) {
			this.clearHintPopup();
			return;
		}
		let i = this.draw.getOriginalElementList(), a = i[r.index], o = a, s = n.getOriginalPositionList()[r.index], c, l = String(r.index);
		r.isTable && r.tdValueIndex !== void 0 && (c = n.getTableTdByContext(i, {
			...r,
			isTable: !0
		}) || void 0, o = c?.value[r.tdValueIndex], s = c?.positionList?.[r.tdValueIndex], l = `${r.tablePath?.map((e) => `${e.index}:${e.trIndex}:${e.tdIndex}`).join("/")}:${r.tdValueIndex}`);
		let u = this._getElementHint(o);
		if (!u && c?.hint && (u = c.hint), !u && a?.hint && (u = a.hint), !u || !o && !c) {
			this.clearHintPopup();
			return;
		}
		this.lastHoverKey !== l && (this.drawHintPopup({
			hint: u,
			position: s,
			td: c
		}, this.draw.getPageNo()), this.lastHoverKey = l);
	}
}, Ci = class {
	draw;
	options;
	container;
	tracePopupContainer;
	listDom;
	lastHoverKey;
	strikeoutState = null;
	underlineState = null;
	currentRow = null;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer(), this.lastHoverKey = "";
		let { popup: t, listDom: n } = this._createTracePopupDom();
		this.tracePopupContainer = t, this.listDom = n;
	}
	_createTracePopupDom() {
		let e = document.createElement("div");
		e.classList.add("ce-trace-popup");
		let t = document.createElement("div");
		return t.classList.add("ce-trace-popup__list"), e.append(t), this.container.append(e), {
			popup: e,
			listDom: t
		};
	}
	drawTracePopup(e, t, n) {
		let r = e.trace;
		if (!r?.length || !t) {
			this.clearTracePopup();
			return;
		}
		let { coordinate: { leftTop: [i, a] }, lineHeight: o } = t, { x: s, y: c } = this.draw.getPageOffset(n);
		this.tracePopupContainer.style.display = "block", this.tracePopupContainer.style.left = `${i + s}px`, this.tracePopupContainer.style.top = `${a + c + o}px`;
		let { insertColor: l, deleteColor: u } = this.options.trace, d = this.draw.getI18n(), f = d.t("trace.author"), p = d.t("trace.time");
		this.listDom.innerHTML = "";
		let m = document.createDocumentFragment();
		for (let e of r) {
			let t = e.type === J.INSERTED, n = document.createElement("div");
			n.classList.add("ce-trace-popup__item");
			let r = document.createElement("span");
			if (r.classList.add("ce-trace-popup__type"), r.innerText = d.t(t ? "trace.insert" : "trace.delete"), r.style.color = t ? l : u, n.append(r), e.author) {
				let t = document.createElement("span");
				t.classList.add("ce-trace-popup__author"), t.innerText = `${f}: ${e.author}`, n.append(t);
			}
			if (e.timestamp) {
				let t = document.createElement("span");
				t.classList.add("ce-trace-popup__time"), t.innerText = `${p}: ${new Date(e.timestamp).toLocaleString()}`, n.append(t);
			}
			m.append(n);
		}
		this.listDom.append(m);
	}
	clearTracePopup() {
		this.tracePopupContainer.style.display = "none", this.lastHoverKey = "";
	}
	handleMouseMove(e) {
		if (!this.draw.isTraceMode()) return;
		let t = e.target.dataset.index;
		t && this.draw.setPageNo(Number(t));
		let n = this.draw.getPosition(), r = n.getPositionByXY({
			x: e.offsetX,
			y: e.offsetY
		});
		if (!~r.index) {
			this.clearTracePopup();
			return;
		}
		let i = this.draw.getOriginalElementList(), a = i[r.index], o = n.getOriginalPositionList()[r.index], s = String(r.index);
		if (r.isTable && r.tdValueIndex !== void 0) {
			let e = n.getTableTdByContext(i, {
				...r,
				isTable: !0
			});
			a = e?.value[r.tdValueIndex], o = e?.positionList?.[r.tdValueIndex], s = `${r.tablePath?.map((e) => `${e.index}:${e.trIndex}:${e.tdIndex}`).join("/")}:${r.tdValueIndex}`;
		}
		if (!a?.trace?.length) {
			this.clearTracePopup();
			return;
		}
		this.lastHoverKey !== s && (this.drawTracePopup(a, o, this.draw.getPageNo()), this.lastHoverKey = s);
	}
	_getTraceFlags(e) {
		let t = e?.trace || [];
		return {
			hasInsert: t.some((e) => e.type === J.INSERTED),
			hasDelete: t.some((e) => e.type === J.DELETED)
		};
	}
	render(e) {
		if (!this.draw.isTraceMode()) return;
		let { ctx: t, element: n, x: r, y: i, curRow: a, metrics: o, offsetY: s, scale: c } = e;
		this.currentRow !== a && (this._flushStrikeout(t, c), this._flushUnderline(t, c), this.currentRow = a);
		let { hasInsert: l, hasDelete: u } = this._getTraceFlags(n);
		if (u) {
			let e = this.draw.getTextParticle().measureBasisWord(t, this.draw.getElementFont(n)), a = i + s + e.actualBoundingBoxDescent * c - o.height / 2;
			n.type === H.SUBSCRIPT ? a += this.draw.getSubscriptParticle().getOffsetY(n) : n.type === H.SUPERSCRIPT && (a += this.draw.getSuperscriptParticle().getOffsetY(n)), this.strikeoutState ? this.strikeoutState.width += o.width : this.strikeoutState = {
				x: r,
				y: a + .5,
				width: o.width
			};
		} else this.strikeoutState && this._flushStrikeout(t, c);
		if (l) {
			let e = this.draw.getElementRowMargin(n), t = n.left || 0, s = 0;
			n.type === H.SUBSCRIPT && (s = this.draw.getSubscriptParticle().getOffsetY(n));
			let l = r - t, u = Math.floor(i + a.height - e + s + 2 * c) + .5;
			this.underlineState ? this.underlineState.width += o.width + t : this.underlineState = {
				x: l,
				y: u,
				width: o.width + t
			};
		} else this.underlineState && this._flushUnderline(t, c);
	}
	flush(e) {
		let t = this.options.scale;
		this._flushStrikeout(e, t), this._flushUnderline(e, t), this.currentRow = null;
	}
	_flushStrikeout(e, t) {
		this.strikeoutState &&= (e.save(), e.lineWidth = this.options.trace.lineWidth * t, e.strokeStyle = this.options.trace.deleteColor, e.lineCap = "butt", e.beginPath(), e.moveTo(this.strikeoutState.x, this.strikeoutState.y), e.lineTo(this.strikeoutState.x + this.strikeoutState.width, this.strikeoutState.y), e.stroke(), e.restore(), null);
	}
	_flushUnderline(e, t) {
		this.underlineState &&= (e.save(), e.lineWidth = this.options.trace.lineWidth * t, e.strokeStyle = this.options.trace.insertColor, e.lineCap = "butt", e.beginPath(), e.moveTo(this.underlineState.x, this.underlineState.y), e.lineTo(this.underlineState.x + this.underlineState.width, this.underlineState.y), e.stroke(), e.restore(), null);
	}
	isTraceHidden(e) {
		let t = e.trace;
		return t?.[t.length - 1]?.type === J.DELETED && !this.draw.isTraceMode();
	}
	_markElementList(e, t) {
		if (this.options.trace.disabled) return;
		let n = this.options.trace.author, r = Date.now();
		Gn(e, (e) => {
			let i = e.trace || [];
			i[i.length - 1]?.type !== t && (e.trace = [...i, {
				type: t,
				author: n,
				timestamp: r
			}]);
		});
	}
	markElementListInserted(e) {
		this._markElementList(e, J.INSERTED);
	}
	markElementListDeleted(e, t) {
		let n = e;
		if (!t?.isIgnoreDeletedRule && !this.draw.isDesignMode() && !this.draw.getControl().getIsRangeWithinControl()) {
			let r = this.draw.getMode(), i = t?.tdDeletable ?? this.draw.getTd()?.deletable, { group: a, modeRule: o } = this.options;
			n = e.filter((e) => e.hide || e.control?.hide || e.area?.hide || i !== !1 && e.control?.deletable !== !1 && (!e.controlId || r !== p.FORM || !o[r].controlDeletableDisabled) && e.title?.deletable !== !1 && (a.deletable !== !1 || !e.groupIds?.length) && (e.area?.deletable !== !1 || e.areaIndex !== 0));
		}
		return this._markElementList(n, J.DELETED), n;
	}
}, wi = class {
	options;
	constructor(e) {
		this.options = e.getOptions();
	}
	render(e, t, n, r) {
		let { scale: i, label: { defaultBackgroundColor: a, defaultColor: o, defaultBorderRadius: s, defaultPadding: c } } = this.options, l = t.label?.backgroundColor || a, u = t.label?.color || o, d = t.label?.borderRadius || s, f = t.label?.padding || c;
		e.save(), e.font = t.style;
		let { width: p, height: m, boundingBoxAscent: h } = t.metrics;
		e.fillStyle = l, this._drawRoundedRect(e, n, r - h, p, m + (f[0] + f[3]) * i, d * i), e.fill(), e.fillStyle = u, e.fillText(t.value, n + f[3] * i, r), e.restore();
	}
	_drawRoundedRect(e, t, n, r, i, a) {
		e.beginPath(), e.moveTo(t + a, n), e.lineTo(t + r - a, n), e.quadraticCurveTo(t + r, n, t + r, n + a), e.lineTo(t + r, n + i - a), e.quadraticCurveTo(t + r, n + i, t + r - a, n + i), e.lineTo(t + a, n + i), e.quadraticCurveTo(t, n + i, t, n + i - a), e.lineTo(t, n + a), e.quadraticCurveTo(t, n, t + a, n), e.closePath();
	}
}, Ti = class {
	draw;
	position;
	zone;
	options;
	elementList;
	layoutMap;
	constructor(e, t) {
		this.draw = e, this.position = e.getPosition(), this.zone = e.getZone(), this.options = e.getOptions(), this.elementList = t || [], this.layoutMap = /* @__PURE__ */ new Map();
	}
	getRowList() {
		return this._getLayoutByDirection(this.options.paperDirection)[0];
	}
	setElementList(e) {
		this.elementList = e;
	}
	getElementList() {
		return this.elementList;
	}
	getPositionList(e = this.options.paperDirection) {
		return this._getLayoutByDirection(e)[1];
	}
	compute() {
		this.recovery(), this._getLayoutByDirection(this.options.paperDirection);
	}
	recovery() {
		this.layoutMap.clear();
	}
	_getLayoutByDirection(e) {
		let t = this.layoutMap.get(e);
		if (!t) {
			let n = this._computeRowList(e);
			t = [n, []], this.layoutMap.set(e, t), t[1] = this._computePositionList(e, n);
		}
		return t;
	}
	_computeRowList(e) {
		let t = this.draw.getMargins(e), n = this.draw.getInnerWidth(e), r = Bn(this.elementList);
		return this.draw.computeRowList({
			startX: t[3],
			startY: this.getHeaderTop(),
			innerWidth: n,
			elementList: this.elementList,
			surroundElementList: r
		});
	}
	_computePositionList(e, t) {
		let n = this.draw.getMargins(e), r = [];
		return this.position.computePageRowPosition({
			positionList: r,
			rowList: t,
			pageNo: 0,
			startRowIndex: 0,
			startIndex: 0,
			startX: n[3],
			startY: this.getHeaderTop(),
			innerWidth: this.draw.getInnerWidth(e),
			zone: m.HEADER
		}), r;
	}
	getHeaderTop(e) {
		if (this.isDisabled(e)) return 0;
		let { header: { top: t }, scale: n } = this.options;
		return Math.floor(t * n);
	}
	getMaxHeight(e) {
		let { header: { maxHeightRadio: t } } = this.options, n = this.draw.getHeight(e);
		return Math.floor(n * c[t]);
	}
	getHeight(e, t) {
		if (this.isDisabled(e)) return 0;
		let n = this._resolveDirection(e, t), r = this.getMaxHeight(n), i = this.getRowHeight(n);
		return i > r ? r : i;
	}
	getRowHeight(e = this.options.paperDirection) {
		return this._getLayoutByDirection(e)[0].reduce((e, t) => e + t.height, 0);
	}
	getExtraHeight(e, t) {
		let n = this._resolveDirection(e, t), r = this.draw.getMargins(n), i = this.getHeight(e, n), a = this.getHeaderTop(e) + i - r[0];
		return a <= 0 ? 0 : a;
	}
	_resolveDirection(e, t) {
		return t ?? (e === void 0 ? this.options.paperDirection : this.draw.getPageDirection(e));
	}
	isDisabled(e) {
		return !!(this.options.header.disabled || e !== void 0 && this.options.header.disabledPages.includes(e));
	}
	render(e, t) {
		if (this.options.header.disabledPages.includes(t)) return;
		e.save(), e.globalAlpha = this.zone.isHeaderActive() ? 1 : this.options.header.inactiveAlpha;
		let n = this.draw.getPageDirection(t), r = this.draw.getInnerWidth(n), i = this.getMaxHeight(n), [a, o] = this._getLayoutByDirection(n), s = [], c = 0;
		for (let e = 0; e < a.length; e++) {
			let t = a[e];
			if (c + t.height > i) break;
			s.push(t), c += t.height;
		}
		this.draw.drawRow(e, {
			elementList: this.elementList,
			positionList: o,
			rowList: s,
			pageNo: t,
			startIndex: 0,
			innerWidth: r,
			zone: m.HEADER
		}), e.restore();
	}
}, Ei = class {
	getOffsetY(e) {
		return -e.metrics.height / 2;
	}
	render(e, t, n, r) {
		e.save(), e.font = t.style, t.color && (e.fillStyle = t.color), e.fillText(t.value, n, r + this.getOffsetY(t)), e.restore();
	}
}, Di = class {
	getOffsetY(e) {
		return e.metrics.height / 2;
	}
	render(e, t, n, r) {
		e.save(), e.font = t.style, t.color && (e.fillStyle = t.color), e.fillText(t.value, n, r + this.getOffsetY(t)), e.restore();
	}
}, Oi = class {
	options;
	constructor(e) {
		this.options = e.getOptions();
	}
	render(e, t, n, r) {
		e.save();
		let { scale: i, separator: { lineWidth: a, strokeStyle: o } } = this.options;
		e.lineWidth = (t.lineWidth || a) * i, e.strokeStyle = t.color || o, t.dashArray?.length && e.setLineDash(t.dashArray);
		let s = Math.round(r);
		e.translate(0, e.lineWidth / 2), e.beginPath(), e.moveTo(n, s), e.lineTo(n + t.width * i, s), e.stroke(), e.restore();
	}
}, ki = class {
	draw;
	options;
	i18n;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.i18n = e.getI18n();
	}
	render(e, t, n, r) {
		let { pageBreak: { font: i, fontSize: a, lineDash: o } } = this.options, s = this.i18n.t("pageBreak.displayName"), { scale: c, defaultRowMargin: l } = this.options, u = a * c, d = t.width * c, f = this.draw.getDefaultBasicRowMarginHeight() * l;
		e.save(), e.font = `${u}px ${i}`;
		let p = e.measureText(s), m = (d - p.width) / 2;
		e.setLineDash(o), e.translate(0, .5 + f), e.beginPath(), e.moveTo(n, r), e.lineTo(n + m, r), e.moveTo(n + m + p.width, r), e.lineTo(n + d, r), e.stroke(), e.fillText(s, n + m, r + p.actualBoundingBoxAscent - u / 2), e.restore();
	}
}, Ai = class {
	draw;
	options;
	imageCache;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.imageCache = /* @__PURE__ */ new Map();
	}
	renderText(e, t) {
		let { watermark: { data: n, opacity: r, font: i, size: a, color: o, repeat: s, gap: c, numberType: l }, scale: u } = this.options, { width: d, height: f } = this.draw.getPageSize(t);
		e.save(), e.globalAlpha = r, e.font = `${a * u}px ${i}`;
		let p = n, m = new RegExp(Wt.PAGE_NO);
		m.test(p) && (p = fi.formatNumberPlaceholder(p, t + 1, m, l));
		let h = new RegExp(Wt.PAGE_COUNT);
		h.test(p) && (p = fi.formatNumberPlaceholder(p, this.draw.getPageCount(), h, l));
		let g = e.measureText(p);
		if (s) {
			let t = this.draw.getPagePixelRatio(), n = document.createElement("canvas"), r = n.getContext("2d"), s = g.width, l = g.actualBoundingBoxAscent + g.actualBoundingBoxDescent, m = Math.sqrt(s ** 2 + l ** 2), h = m + 2 * c[0] * u, _ = m + 2 * c[1] * u;
			n.width = h, n.height = _, n.style.width = `${h * t}px`, n.style.height = `${_ * t}px`, r.translate(h / 2, _ / 2), r.rotate(-45 * Math.PI / 180), r.translate(-h / 2, -_ / 2), r.font = `${a * u}px ${i}`, r.fillStyle = o, r.fillText(p, (h - s) / 2, (_ - l) / 2 + g.actualBoundingBoxAscent);
			let v = e.createPattern(n, "repeat");
			v && (e.fillStyle = v, e.fillRect(0, 0, d, f));
		} else {
			let t = d / 2, n = f / 2;
			e.fillStyle = o, e.translate(t, n), e.rotate(-45 * Math.PI / 180), e.fillText(p, -g.width / 2, g.actualBoundingBoxAscent - a * u / 2);
		}
		e.restore();
	}
	renderImage(e, t) {
		let { watermark: { width: n, height: r, data: i, opacity: a, repeat: o, gap: s }, scale: c } = this.options;
		if (!this.imageCache.has(i)) {
			let e = new Image();
			e.setAttribute("crossOrigin", "Anonymous"), e.src = i, e.onload = () => {
				this.imageCache.set(i, e), this.draw.render({
					isCompute: !1,
					isSubmitHistory: !1
				});
			};
			return;
		}
		let { width: l, height: u } = this.draw.getPageSize(t), d = n * c, f = r * c;
		if (e.save(), e.globalAlpha = a, o) {
			let t = this.draw.getPagePixelRatio(), n = document.createElement("canvas"), r = n.getContext("2d"), a = Math.sqrt(d ** 2 + f ** 2), o = a + 2 * s[0] * c, p = a + 2 * s[1] * c;
			n.width = o, n.height = p, n.style.width = `${o * t}px`, n.style.height = `${p * t}px`, r.translate(o / 2, p / 2), r.rotate(-45 * Math.PI / 180), r.translate(-o / 2, -p / 2), r.drawImage(this.imageCache.get(i), (o - d) / 2, (p - f) / 2, d, f);
			let m = e.createPattern(n, "repeat");
			m && (e.fillStyle = m, e.fillRect(0, 0, l, u));
		} else {
			let t = l / 2, n = u / 2;
			e.translate(t, n), e.rotate(-45 * Math.PI / 180), e.drawImage(this.imageCache.get(i), -d / 2, -f / 2, d, f);
		}
		e.restore();
	}
	render(e, t) {
		this.options.watermark.type === Xt.IMAGE ? this.renderImage(e, t) : this.renderText(e, t);
	}
}, ji = class {
	draw;
	control;
	options;
	highlightList;
	highlightMatchResult;
	constructor(e) {
		this.draw = e.getDraw(), this.control = e, this.options = this.draw.getOptions(), this.highlightList = [], this.highlightMatchResult = [];
	}
	getControlHighlight(e, t) {
		let { control: { activeBackgroundColor: n, disabledBackgroundColor: r, existValueBackgroundColor: i, noValueBackgroundColor: a } } = this.options, o = e[t], s = this.draw.isPrintMode(), c = this.control.getActiveControl()?.getElement(), l = !1, u = !1, d = !1, f = !1;
		return o.highlight || (l = !s && !!n && !!c && o.controlId === c.controlId && !this.control.getIsRangeInPostfix()), l || (u = !s && !!r && !!o.control?.disabled), u || (d = !s && !!i && !!o.controlId && this.control.getIsExistValueByElementListIndex(e, t)), d || (f = !s && !!a && !!o.controlId && !this.control.getIsExistValueByElementListIndex(e, t)), (l ? n : "") || (u ? r : "") || (d ? i : "") || (f ? a : "");
	}
	getHighlightMatchResult() {
		return this.highlightMatchResult;
	}
	getHighlightList() {
		return this.highlightList;
	}
	setHighlightList(e) {
		this.highlightList = e;
	}
	computeHighlightList() {
		let e = this.draw.getSearch(), t = (n, r) => {
			let i = 0;
			for (; i < n.length;) {
				let a = n[i];
				if (i++, a.type === H.TABLE) {
					let e = a.trList;
					for (let n = 0; n < e.length; n++) {
						let r = e[n];
						for (let e = 0; e < r.tdList.length; e++) {
							let o = r.tdList[e], s = {
								tableId: a.id,
								tableIndex: i - 1,
								trIndex: n,
								tdIndex: e,
								tdId: o.id
							};
							t(o.value, s);
						}
					}
				}
				let o = a?.control;
				if (!o) continue;
				let s = this.highlightList.findIndex((e) => e.id === a.controlId || o.conceptId && o.conceptId === e.conceptId);
				if (!~s) continue;
				let c = i, l = i;
				for (; l < n.length && n[l].controlId === a.controlId;) l++;
				i = l;
				let u = n.slice(c, l).map((e) => e.controlComponent === K.VALUE ? e : { value: "​" }), { ruleList: d } = this.highlightList[s];
				for (let t = 0; t < d.length; t++) {
					let n = d[t], i = e.getMatchList(n.keyword, u);
					this.highlightMatchResult.push(...i.map((e) => ({
						...e,
						...n,
						...r,
						index: e.index + c
					})));
				}
			}
		};
		this.highlightMatchResult = [], t(this.draw.getOriginalMainElementList());
	}
	renderHighlightList(e, t) {
		if (!this.highlightMatchResult?.length) return;
		let { searchMatchAlpha: n, searchMatchColor: r } = this.options, i = this.draw.getPosition().getOriginalPositionList(), a = this.draw.getOriginalElementList();
		e.save();
		for (let o = 0; o < this.highlightMatchResult.length; o++) {
			let s = this.highlightMatchResult[o], c = null;
			if (s.tableId) {
				let { tableIndex: e, trIndex: t, tdIndex: n, index: r } = s;
				c = a[e]?.trList[t].tdList[n]?.positionList[r];
			} else c = i[s.index];
			if (!c) continue;
			let { coordinate: { leftTop: l, leftBottom: u, rightTop: d }, pageNo: f } = c;
			if (f !== t) continue;
			e.fillStyle = s.backgroundColor || r, e.globalAlpha = s.alpha || n;
			let p = l[0], m = l[1], h = d[0] - l[0], g = u[1] - l[1];
			e.fillRect(p, m, h, g);
		}
		e.restore();
	}
}, Mi = class {
	borderRect;
	options;
	constructor(e) {
		this.borderRect = this.clearBorderInfo(), this.options = e.getOptions();
	}
	clearBorderInfo() {
		return this.borderRect = {
			x: 0,
			y: 0,
			width: 0,
			height: 0
		}, this.borderRect;
	}
	recordBorderInfo(e, t, n, r) {
		this.borderRect.width || (this.borderRect.x = e, this.borderRect.y = t, this.borderRect.height = r), this.borderRect.width += n;
	}
	render(e) {
		if (!this.borderRect.width) return;
		let { scale: t, control: { borderWidth: n, borderColor: r } } = this.options, { x: i, y: a, width: o, height: s } = this.borderRect;
		e.save(), e.translate(0, 1 * t), e.lineWidth = n * t, e.strokeStyle = r, e.beginPath(), e.rect(i, a, o, s), e.stroke(), e.restore(), this.clearBorderInfo();
	}
}, Ni = class {
	draw;
	element;
	control;
	isPopup;
	selectDom;
	options;
	VALUE_DELIMITER = ",";
	DEFAULT_MULTI_SELECT_DELIMITER = ",";
	constructor(e, t) {
		let n = t.getDraw();
		this.draw = n, this.options = n.getOptions(), this.element = e, this.control = t, this.isPopup = !1, this.selectDom = null;
	}
	setElement(e) {
		this.element = e;
	}
	getElement() {
		return this.element;
	}
	getIsPopup() {
		return this.isPopup;
	}
	getCodes() {
		return this.element?.control?.code ? this.element.control.code.split(",") : [];
	}
	getText(e) {
		if (!this.element?.control) return null;
		let t = this.element.control;
		if (!t.valueSets?.length) return null;
		let n = t?.multiSelectDelimiter || this.DEFAULT_MULTI_SELECT_DELIMITER, r = t.valueSets, i = [];
		return e.forEach((e) => {
			let t = r.find((t) => t.code === e);
			t && !de(t.value) && i.push(t.value);
		}), i.join(n) || null;
	}
	getValue(e = {}) {
		let t = e.elementList || this.control.getElementList(), { startIndex: n } = e.range || this.control.getRange(), r = t[n], i = [], a = n;
		for (; a > 0;) {
			let e = t[a];
			if (e.controlId !== r.controlId || e.controlComponent === K.PREFIX || e.controlComponent === K.PRE_TEXT) break;
			e.controlComponent === K.VALUE && !hn(e) && i.unshift(e), a--;
		}
		let o = n + 1;
		for (; o < t.length;) {
			let e = t[o];
			if (e.controlId !== r.controlId || e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT) break;
			e.controlComponent === K.VALUE && !hn(e) && i.push(e), o++;
		}
		return i;
	}
	setValue(e, t = {}, n = {}) {
		if (!this.element.control?.selectExclusiveOptions?.inputAble || !n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return -1;
		let r = t.elementList || this.control.getElementList(), i = t.range || this.control.getRange();
		this.control.shrinkBoundary(t);
		let { startIndex: a, endIndex: o } = i, s = this.control.getDraw();
		a === o ? this.control.removePlaceholder(a, t) : s.deleteElementList(r, a + 1, o - a, { isIgnoreDeletedRule: n.isIgnoreDeletedRule });
		let c = r[a], l = c.type && !Be.includes(c.type) || c.controlComponent === K.PREFIX || c.controlComponent === K.PRE_TEXT ? V(c, [
			"control",
			"controlId",
			...Le
		]) : ae(c, ["type"]), u = i.startIndex + 1;
		for (let t = 0; t < e.length; t++) {
			let n = {
				...l,
				...e[t],
				controlComponent: K.VALUE
			};
			kn(r, [n], a, { editorOptions: this.options }), s.getTraceParticle().markElementListInserted([n]), s.spliceElementList(r, u + t, 0, [n]);
		}
		return u + e.length - 1;
	}
	keydown(e) {
		if (this.control.getIsDisabledControl()) return null;
		let t = this.control.getElementList(), n = this.control.getRange();
		this.control.shrinkBoundary();
		let { startIndex: r, endIndex: i } = n, a = t[r], o = t[i], s = this.element.control?.selectExclusiveOptions?.inputAble;
		if (e.key === Z.Backspace) return r === i ? a.controlComponent === K.PREFIX || a.controlComponent === K.PRE_TEXT || o.controlComponent === K.POSTFIX || o.controlComponent === K.POST_TEXT || a.controlComponent === K.PLACEHOLDER ? this.control.removeControl(r) : s ? (this.draw.deleteElementList(t, r, 1), this.getValue().length || this.control.addPlaceholder(r - 1), r - 1) : this.clearSelect() : s ? (this.draw.deleteElementList(t, r + 1, i - r), this.getValue().length || this.control.addPlaceholder(r), r) : this.clearSelect();
		if (e.key === Z.Delete) {
			if (r !== i) return s ? (this.draw.deleteElementList(t, r + 1, i - r), this.getValue().length || this.control.addPlaceholder(r), r) : this.clearSelect();
			{
				let e = t[i + 1];
				return (a.controlComponent === K.PREFIX || a.controlComponent === K.PRE_TEXT) && e.controlComponent === K.PLACEHOLDER || e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT || a.controlComponent === K.PLACEHOLDER ? this.control.removeControl(r) : s ? (this.draw.deleteElementList(t, r + 1, 1), this.getValue().length || this.control.addPlaceholder(r), r) : this.clearSelect();
			}
		}
		return i;
	}
	cut() {
		if (this.control.getIsDisabledControl()) return -1;
		this.control.shrinkBoundary();
		let { startIndex: e, endIndex: t } = this.control.getRange();
		return e === t ? e : this.clearSelect();
	}
	clearSelect(e = {}, t = {}) {
		let { isIgnoreDisabledRule: n = !1, isAddPlaceholder: r = !0 } = t;
		if (!n && this.control.getIsDisabledControl(e)) return -1;
		let i = e.elementList || this.control.getElementList(), { startIndex: a } = e.range || this.control.getRange(), o = i[a], s = -1, c = -1, l = a;
		for (; l > 0;) {
			let e = i[l];
			if (e.controlId !== o.controlId || e.controlComponent === K.PREFIX || e.controlComponent === K.PRE_TEXT) {
				s = l;
				break;
			}
			l--;
		}
		let u = a + 1;
		for (; u < i.length;) {
			let e = i[u];
			if (e.controlId !== o.controlId || e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT) {
				c = u - 1;
				break;
			}
			u++;
		}
		if (!~s || !~c) return -1;
		let d = this.control.getDraw(), f = s + 1, p = this.control.removePlaceholderInRange(i, f, c - s);
		return d.deleteElementList(i, f, p, { isIgnoreDeletedRule: t.isIgnoreDeletedRule }), r && this.control.addPlaceholder(l, e), this.control.setControlProperties({ code: null }, {
			elementList: i,
			range: {
				startIndex: l,
				endIndex: l
			}
		}), l;
	}
	setSelect(e, t = {}, n = {}) {
		if (!n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return;
		let r = t.elementList || this.control.getElementList(), i = t.range || this.control.getRange(), a = this.element.control, o = e?.split(this.VALUE_DELIMITER) || [], s = a.code, c = a.code?.split(this.VALUE_DELIMITER) || [], l = a.isMultiSelect;
		if (!l && e === s || l && ce(c, o)) {
			this.control.repaintControl({
				curIndex: i.startIndex,
				isCompute: !1,
				isSubmitHistory: !1
			}), this.destroy();
			return;
		}
		let u = a.valueSets;
		if (!Array.isArray(u) || !u.length) return;
		let d = this.getText(o);
		if (!d) {
			if (s) {
				let e = this.clearSelect(t, { isIgnoreDeletedRule: n.isIgnoreDeletedRule });
				~e && (this.control.repaintControl({ curIndex: e }), this.control.emitControlContentChange({ controlValue: [] }));
			}
			return;
		}
		let f = this.getValue(t)[0], p = f ? V(f, Te) : V(r[i.startIndex], Le), m = this.clearSelect(t, {
			isAddPlaceholder: !1,
			isIgnoreDeletedRule: n.isIgnoreDeletedRule
		});
		if (!~m) return;
		s || this.control.removePlaceholder(m, t);
		let h = ae(r[m], Te), g = m + 1, _ = N(d), v = this.control.getDraw();
		for (let e = 0; e < _.length; e++) {
			let t = {
				...p,
				...h,
				type: H.TEXT,
				value: _[e],
				controlComponent: K.VALUE
			};
			kn(r, [t], m, { editorOptions: this.options }), v.getTraceParticle().markElementListInserted([t]), v.spliceElementList(r, g + e, 0, [t]);
		}
		if (this.control.setControlProperties({ code: e }, {
			elementList: r,
			range: {
				startIndex: m,
				endIndex: m
			}
		}), !t.range) {
			let e = g + _.length - 1;
			this.control.repaintControl({ curIndex: e }), this.control.emitControlContentChange({ context: t }), l || this.destroy();
		}
	}
	_createSelectPopupDom() {
		let e = this.element.control, t = e.valueSets;
		if (!Array.isArray(t) || !t.length) return;
		let n = this.control.getPosition();
		if (!n) return;
		let r = document.createElement("div");
		r.classList.add("ce-select-control-popup"), r.setAttribute(_e, d.POPUP);
		let i = document.createElement("ul"), a = null;
		for (let n = 0; n < t.length; n++) {
			let r = t[n], o = document.createElement("li"), s = this.getCodes();
			s.includes(r.code) && (o.classList.add("active"), a = o), o.onclick = () => {
				let t = s.findIndex((e) => e === r.code);
				e.isMultiSelect ? ~t ? s.splice(t, 1) : s.push(r.code) : s = ~t ? [] : [r.code], this.setSelect(s.join(this.VALUE_DELIMITER));
			}, o.append(document.createTextNode(r.value)), i.append(o);
		}
		r.append(i);
		let { coordinate: { leftTop: [o, s] }, lineHeight: c } = n, l = this.control.getPreY();
		r.style.left = `${o + this.control.getPreX()}px`, r.style.top = `${s + l + c}px`, this.control.getContainer().append(r), this.selectDom = r, a && he(r, a);
	}
	awake() {
		if (this.isPopup || this.control.getIsDisabledControl() || !this.control.getIsRangeWithinControl()) return;
		let { startIndex: e } = this.control.getRange();
		this.control.getElementList()[e + 1]?.controlId === this.element.controlId && (this._createSelectPopupDom(), this.isPopup = !0);
	}
	destroy() {
		this.isPopup &&= (this.selectDom?.remove(), !1);
	}
}, Pi = class {
	element;
	control;
	options;
	constructor(e, t) {
		let n = t.getDraw();
		this.options = n.getOptions(), this.element = e, this.control = t;
	}
	setElement(e) {
		this.element = e;
	}
	getElement() {
		return this.element;
	}
	getValue(e = {}) {
		let t = e.elementList || this.control.getElementList(), { startIndex: n } = e.range || this.control.getRange(), r = t[n], i = [];
		r.controlComponent === K.VALUE && !hn(r) && i.push(r);
		let a = n;
		for (; a > 0;) {
			let e = Un(t, a, -1, r.controlId);
			if (e < 0) break;
			let n = t[e];
			if (n.controlId !== r.controlId || n.controlComponent === K.PREFIX || n.controlComponent === K.PRE_TEXT) break;
			n.controlComponent === K.VALUE && !hn(n) && i.unshift(n), a = e;
		}
		let o = n + 1;
		for (; o < t.length;) {
			let e = Un(t, o, 1, r.controlId);
			if (e < 0 || e >= t.length) break;
			let n = t[e];
			if (n.controlId !== r.controlId || n.controlComponent === K.POSTFIX || n.controlComponent === K.POST_TEXT) break;
			n.controlComponent === K.VALUE && !hn(n) && i.push(n), o = e;
		}
		return i;
	}
	setValue(e, t = {}, n = {}) {
		if (!n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return -1;
		let r = t.elementList || this.control.getElementList(), i = t.range || this.control.getRange();
		this.control.shrinkBoundary(t);
		let { startIndex: a, endIndex: o } = i, s = this.control.getDraw(), c = r[a], l = this.control.getActiveControl()?.getElement();
		if (l && l.controlId && l.controlId !== c.controlId) {
			let e = !1;
			for (let t = a; t <= o; t++) if (r[t]?.controlId === l.controlId) {
				e = !0;
				break;
			}
			e && this.control.destroyControl({ isEmitEvent: !0 });
		}
		a === o ? this.control.removePlaceholder(a, t) : s.deleteElementList(r, a + 1, o - a, { isIgnoreDeletedRule: n.isIgnoreDeletedRule });
		let u = c.type && !Be.includes(c.type) || c.controlComponent === K.PREFIX || c.controlComponent === K.PRE_TEXT ? V(c, [
			"control",
			"controlId",
			...Le
		]) : ae(c, ["type"]), d = i.startIndex + 1;
		for (let t = 0; t < e.length; t++) {
			let n = {
				...u,
				...e[t],
				controlComponent: K.VALUE
			};
			kn(r, [n], a, { editorOptions: this.options }), s.getTraceParticle().markElementListInserted([n]), s.spliceElementList(r, d + t, 0, [n]);
		}
		return d + e.length - 1;
	}
	clearValue(e = {}, t = {}) {
		if (!t.isIgnoreDisabledRule && this.control.getIsDisabledControl(e)) return -1;
		let n = e.elementList || this.control.getElementList(), r = e.range || this.control.getValueRange() || this.control.getRange(), { startIndex: i, endIndex: a } = r, o = i + 1, s = this.control.removePlaceholderInRange(n, o, a - i);
		return this.control.getDraw().deleteElementList(n, o, s, { isIgnoreDeletedRule: t.isIgnoreDeletedRule }), this.getValue({
			range: r,
			elementList: n
		}).length || this.control.addPlaceholder(i, e), i;
	}
	keydown(e) {
		if (this.control.getIsDisabledControl()) return null;
		let t = this.control.getElementList(), n = this.control.getRange();
		this.control.shrinkBoundary();
		let { startIndex: r, endIndex: i } = n, a = t[r], o = t[i], s = this.control.getDraw();
		if (e.key === Z.Backspace) return r === i ? a.controlComponent === K.PREFIX || a.controlComponent === K.PRE_TEXT || o.controlComponent === K.POSTFIX || o.controlComponent === K.POST_TEXT || a.controlComponent === K.PLACEHOLDER ? this.control.removeControl(r) : (s.deleteElementList(t, r, 1), this.getValue().length || this.control.addPlaceholder(r - 1), r - 1) : (s.deleteElementList(t, r + 1, i - r), this.getValue().length || this.control.addPlaceholder(r), r);
		if (e.key === Z.Delete) {
			if (r !== i) return s.deleteElementList(t, r + 1, i - r), this.getValue().length || this.control.addPlaceholder(r), r;
			{
				let e = t[i + 1];
				return (a.controlComponent === K.PREFIX || a.controlComponent === K.PRE_TEXT) && e.controlComponent === K.PLACEHOLDER || e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT || a.controlComponent === K.PLACEHOLDER ? this.control.removeControl(r) : (s.deleteElementList(t, r + 1, 1), this.getValue().length || this.control.addPlaceholder(r), r);
			}
		}
		return i;
	}
	cut() {
		if (this.control.getIsDisabledControl()) return -1;
		this.control.shrinkBoundary();
		let { startIndex: e, endIndex: t } = this.control.getRange();
		if (e === t) return e;
		let n = this.control.getDraw(), r = this.control.getElementList();
		return n.deleteElementList(r, e + 1, t - e), this.getValue().length || this.control.addPlaceholder(e), e;
	}
}, Q;
(function(e) {
	e.DATE = "date", e.MONTH = "month", e.YEAR = "year";
})(Q ||= {});
//#endregion
//#region src/editor/core/draw/particle/date/DatePicker.ts
var Fi = class {
	draw;
	options;
	now;
	dom;
	renderOptions;
	isDatePicker;
	pickDate;
	lang;
	datePickerType;
	viewMode;
	yearPageStart;
	constructor(e, t = {}) {
		this.draw = e, this.options = t, this.lang = this._getLang(), this.now = /* @__PURE__ */ new Date(), this.dom = this._createDom(), this.renderOptions = null, this.isDatePicker = !0, this.pickDate = null, this.datePickerType = Q.DATE, this.viewMode = Q.DATE, this.yearPageStart = 0, this._bindEvent();
	}
	_createDom() {
		let e = document.createElement("div");
		e.classList.add("ce-date-container"), e.setAttribute(_e, d.POPUP);
		let t = document.createElement("div");
		t.classList.add("ce-date-wrap");
		let n = document.createElement("div");
		n.classList.add("ce-date-title");
		let r = document.createElement("span");
		r.classList.add("ce-date-title__pre-year"), r.innerText = "<<";
		let i = document.createElement("span");
		i.classList.add("ce-date-title__pre-month"), i.innerText = "<";
		let a = document.createElement("span");
		a.classList.add("ce-date-title__year-label");
		let o = document.createElement("span");
		o.classList.add("ce-date-title__month-label");
		let s = document.createElement("span");
		s.classList.add("ce-date-title__now"), s.append(a), s.append(o);
		let c = document.createElement("span");
		c.classList.add("ce-date-title__next-month"), c.innerText = ">";
		let l = document.createElement("span");
		l.classList.add("ce-date-title__next-year"), l.innerText = ">>", n.append(r), n.append(i), n.append(s), n.append(c), n.append(l);
		let u = document.createElement("div");
		u.classList.add("ce-date-week");
		let { weeks: { sun: f, mon: p, tue: m, wed: h, thu: g, fri: _, sat: v } } = this.lang;
		[
			f,
			p,
			m,
			h,
			g,
			_,
			v
		].forEach((e) => {
			let t = document.createElement("span");
			t.innerText = `${e}`, u.append(t);
		});
		let y = document.createElement("div");
		y.classList.add("ce-date-day"), t.append(n), t.append(u), t.append(y);
		let b = document.createElement("div");
		b.classList.add("ce-year-wrap");
		let x = document.createElement("div");
		x.classList.add("ce-month-wrap");
		let S = document.createElement("ul");
		S.classList.add("ce-time-wrap");
		let C, w, T;
		[
			this.lang.hour,
			this.lang.minute,
			this.lang.second
		].forEach((e, t) => {
			let n = document.createElement("li"), r = document.createElement("span");
			r.innerText = e, n.append(r);
			let i = document.createElement("ol"), a = t === 0, o = t === 1, s = a ? 24 : 60;
			for (let e = 0; e < s; e++) {
				let t = document.createElement("li");
				t.innerText = `${String(e).padStart(2, "0")}`, t.setAttribute("data-id", `${e}`), i.append(t);
			}
			a ? C = i : o ? w = i : T = i, n.append(i), S.append(n);
		});
		let E = document.createElement("div");
		E.classList.add("ce-date-menu");
		let D = document.createElement("button");
		D.classList.add("ce-date-menu__time"), D.innerText = this.lang.timeSelect;
		let O = document.createElement("button");
		O.classList.add("ce-date-menu__now"), O.innerText = this.lang.now;
		let k = document.createElement("button");
		return k.classList.add("ce-date-menu__submit"), k.innerText = this.lang.confirm, E.append(D), E.append(O), E.append(k), e.append(t), e.append(b), e.append(x), e.append(S), e.append(E), this.draw.getContainer().append(e), {
			container: e,
			dateWrap: t,
			datePickerWeek: u,
			yearWrap: b,
			monthWrap: x,
			timeWrap: S,
			title: {
				preYear: r,
				preMonth: i,
				now: s,
				yearLabel: a,
				monthLabel: o,
				nextMonth: c,
				nextYear: l
			},
			day: y,
			time: {
				hour: C,
				minute: w,
				second: T
			},
			menu: {
				time: D,
				now: O,
				submit: k
			}
		};
	}
	_bindEvent() {
		this.dom.title.preYear.onclick = () => {
			this.viewMode === Q.YEAR ? this._preYearPage() : this._preYear();
		}, this.dom.title.preMonth.onclick = () => {
			this._preMonth();
		}, this.dom.title.nextMonth.onclick = () => {
			this._nextMonth();
		}, this.dom.title.nextYear.onclick = () => {
			this.viewMode === Q.YEAR ? this._nextYearPage() : this._nextYear();
		}, this.dom.title.yearLabel.onclick = (e) => {
			e.stopPropagation(), this.datePickerType === Q.DATE && this.viewMode === Q.DATE && (this.viewMode = Q.YEAR, this._update(), this._switchView());
		}, this.dom.title.monthLabel.onclick = (e) => {
			e.stopPropagation(), this.datePickerType === Q.DATE && this.viewMode === Q.DATE && (this.viewMode = Q.MONTH, this._update(), this._switchView());
		}, this.dom.title.now.onclick = () => {
			this.datePickerType === Q.DATE && (this.viewMode === Q.YEAR || this.viewMode === Q.MONTH) && (this.viewMode = Q.DATE, this._update(), this._switchView());
		}, this.dom.menu.time.onclick = () => {
			this.isDatePicker = !this.isDatePicker, this._toggleDateTimePicker();
		}, this.dom.menu.now.onclick = () => {
			this._now(), this._submit();
		}, this.dom.menu.submit.onclick = () => {
			this.dispose(), this._submit();
		}, this.dom.time.hour.onclick = (e) => {
			if (!this.pickDate) return;
			let t = e.target.dataset.id;
			t && (this.pickDate.setHours(Number(t)), this._setTimePick(!1));
		}, this.dom.time.minute.onclick = (e) => {
			if (!this.pickDate) return;
			let t = e.target.dataset.id;
			t && (this.pickDate.setMinutes(Number(t)), this._setTimePick(!1));
		}, this.dom.time.second.onclick = (e) => {
			if (!this.pickDate) return;
			let t = e.target.dataset.id;
			t && (this.pickDate.setSeconds(Number(t)), this._setTimePick(!1));
		};
	}
	_setPosition() {
		if (!this.renderOptions) return;
		let { position: { coordinate: { leftTop: [e, t] }, lineHeight: n, pageNo: r } } = this.renderOptions, i = r ?? this.draw.getPageNo(), { x: a, y: o } = this.draw.getPageOffset(i);
		this.dom.container.style.left = `${e + a}px`, this.dom.container.style.top = `${t + o + n}px`;
	}
	isInvalidDate(e) {
		return e.toDateString() === "Invalid Date";
	}
	_setValue() {
		let e = this.renderOptions?.value;
		if (e) {
			let t = new Date(e);
			this.now = this.isInvalidDate(t) ? /* @__PURE__ */ new Date() : t;
		} else this.now = /* @__PURE__ */ new Date();
		this.pickDate = new Date(this.now);
	}
	_getDatePickerType(e) {
		if (!e) return Q.DATE;
		let t = /y+/i.test(e), n = /M+/.test(e), r = /[dD]+/.test(e);
		return t && !n && !r ? Q.YEAR : t && n && !r ? Q.MONTH : Q.DATE;
	}
	_getLang() {
		let e = this.draw.getI18n(), t = e.t.bind(e);
		return {
			now: t("datePicker.now"),
			confirm: t("datePicker.confirm"),
			return: t("datePicker.return"),
			timeSelect: t("datePicker.timeSelect"),
			weeks: {
				sun: t("datePicker.weeks.sun"),
				mon: t("datePicker.weeks.mon"),
				tue: t("datePicker.weeks.tue"),
				wed: t("datePicker.weeks.wed"),
				thu: t("datePicker.weeks.thu"),
				fri: t("datePicker.weeks.fri"),
				sat: t("datePicker.weeks.sat")
			},
			year: t("datePicker.year"),
			month: t("datePicker.month"),
			months: {
				jan: t("datePicker.months.jan"),
				feb: t("datePicker.months.feb"),
				mar: t("datePicker.months.mar"),
				apr: t("datePicker.months.apr"),
				may: t("datePicker.months.may"),
				jun: t("datePicker.months.jun"),
				jul: t("datePicker.months.jul"),
				aug: t("datePicker.months.aug"),
				sep: t("datePicker.months.sep"),
				oct: t("datePicker.months.oct"),
				nov: t("datePicker.months.nov"),
				dec: t("datePicker.months.dec")
			},
			hour: t("datePicker.hour"),
			minute: t("datePicker.minute"),
			second: t("datePicker.second")
		};
	}
	_setLangChange() {
		this.dom.menu.time.innerText = this.lang.timeSelect, this.dom.menu.now.innerText = this.lang.now, this.dom.menu.submit.innerText = this.lang.confirm;
		let { weeks: { sun: e, mon: t, tue: n, wed: r, thu: i, fri: a, sat: o } } = this.lang, s = [
			e,
			t,
			n,
			r,
			i,
			a,
			o
		];
		this.dom.datePickerWeek.childNodes.forEach((e, t) => {
			let n = e;
			n.innerText = s[t];
		});
		let c = this.dom.time.hour.previousElementSibling;
		c.innerText = this.lang.hour;
		let l = this.dom.time.minute.previousElementSibling;
		l.innerText = this.lang.minute;
		let u = this.dom.time.second.previousElementSibling;
		u.innerText = this.lang.second;
	}
	_update() {
		this.viewMode === Q.YEAR ? this._updateYearView() : this.viewMode === Q.MONTH ? this._updateMonthView() : this._updateDateView(), this._updateTitleVisibility();
	}
	_updateTitleVisibility() {
		let { preYear: e, preMonth: t, nextMonth: n, nextYear: r } = this.dom.title;
		this.viewMode === Q.YEAR || this.viewMode === Q.MONTH ? (e.style.display = "inline-block", e.innerText = "<<", r.style.display = "inline-block", r.innerText = ">>", t.style.display = "none", n.style.display = "none") : (e.style.display = "inline-block", e.innerText = "<<", t.style.display = "inline-block", t.innerText = "<", n.style.display = "inline-block", n.innerText = ">", r.style.display = "inline-block", r.innerText = ">>");
	}
	_updateDateView() {
		let e = /* @__PURE__ */ new Date(), t = e.getFullYear(), n = e.getMonth() + 1, r = e.getDate(), i = null, a = null, o = null;
		this.pickDate && (i = this.pickDate.getFullYear(), a = this.pickDate.getMonth() + 1, o = this.pickDate.getDate());
		let s = this.now.getFullYear(), c = this.now.getMonth() + 1;
		this.dom.title.yearLabel.innerText = `${s}${this.lang.year}`, this.dom.title.monthLabel.innerText = ` ${String(c).padStart(2, "0")}${this.lang.month}`;
		let l = new Date(s, c, 0).getDate(), u = new Date(s, c - 1, 1).getDay();
		u === 0 && (u = 7);
		let d = new Date(s, c - 1, 0).getDate();
		this.dom.day.innerHTML = "";
		let f = d - u + 1;
		for (let e = f; e <= d; e++) {
			let t = document.createElement("div");
			t.classList.add("disable"), t.innerText = `${e}`, t.onclick = () => {
				let t = c - 2;
				this.now = new Date(s, t, e), this._setDatePick(s, t, e);
			}, this.dom.day.append(t);
		}
		for (let e = 1; e <= l; e++) {
			let l = document.createElement("div");
			t === s && n === c && r === e && l.classList.add("active"), this.pickDate && i === s && a === c && o === e && l.classList.add("select"), l.innerText = `${e}`, l.onclick = (t) => {
				let n = c - 1;
				this.now = new Date(s, n, e), this._setDatePick(s, n, e), t.stopPropagation();
			}, this.dom.day.append(l);
		}
		let p = 42 - u - l;
		for (let e = 1; e <= p; e++) {
			let t = document.createElement("div");
			t.classList.add("disable"), t.innerText = `${e}`, t.onclick = () => {
				this.now = new Date(s, c, e), this._setDatePick(s, c, e);
			}, this.dom.day.append(t);
		}
	}
	_updateYearView() {
		let e = this.now.getFullYear();
		this.yearPageStart === 0 && (this.yearPageStart = e - 5);
		let t = this.yearPageStart, n = t + 11;
		this.dom.title.yearLabel.innerText = `${t} - ${n}`, this.dom.title.monthLabel.innerText = "", this.dom.yearWrap.innerHTML = "";
		let r = this.pickDate?.getFullYear() || null, i = (/* @__PURE__ */ new Date()).getFullYear();
		for (let e = t; e <= n; e++) {
			let t = document.createElement("div");
			t.innerText = `${e}`, e === i && t.classList.add("active"), r === e && t.classList.add("select"), t.onclick = () => {
				this.now.setFullYear(e), this.pickDate && this.pickDate.setFullYear(e), this.datePickerType === Q.YEAR ? (this._submit(), this.dispose()) : (this.viewMode = Q.MONTH, this._update(), this._switchView());
			}, this.dom.yearWrap.append(t);
		}
	}
	_updateMonthView() {
		let e = this.now.getFullYear();
		this.dom.title.yearLabel.innerText = `${e}${this.lang.year}`, this.dom.title.monthLabel.innerText = "", this.dom.monthWrap.innerHTML = "";
		let t = [
			this.lang.months.jan,
			this.lang.months.feb,
			this.lang.months.mar,
			this.lang.months.apr,
			this.lang.months.may,
			this.lang.months.jun,
			this.lang.months.jul,
			this.lang.months.aug,
			this.lang.months.sep,
			this.lang.months.oct,
			this.lang.months.nov,
			this.lang.months.dec
		], n = /* @__PURE__ */ new Date(), r = n.getFullYear(), i = n.getMonth(), a = this.pickDate?.getFullYear() || null, o = this.pickDate?.getMonth() || null;
		for (let n = 0; n < 12; n++) {
			let s = document.createElement("div");
			s.innerText = t[n], r === e && i === n && s.classList.add("active"), a === e && o === n && s.classList.add("select"), s.onclick = () => {
				this.now.setMonth(n), this.pickDate && this.pickDate.setMonth(n), this.datePickerType === Q.MONTH ? (this._submit(), this.dispose()) : (this.viewMode = Q.DATE, this._update(), this._switchView());
			}, this.dom.monthWrap.append(s);
		}
	}
	_switchView() {
		this.dom.yearWrap.classList.remove("active"), this.dom.monthWrap.classList.remove("active"), this.dom.timeWrap.classList.remove("active"), this.dom.dateWrap.classList.remove("year-mode", "month-mode"), this.dom.datePickerWeek.style.display = "flex", this.viewMode === Q.DATE ? this.dom.dateWrap.classList.add("active") : this.viewMode === Q.YEAR ? (this.dom.dateWrap.classList.add("active", "year-mode"), this.dom.yearWrap.classList.add("active"), this.dom.datePickerWeek.style.display = "none") : this.viewMode === Q.MONTH && (this.dom.dateWrap.classList.add("active", "month-mode"), this.dom.monthWrap.classList.add("active"), this.dom.datePickerWeek.style.display = "none"), this.datePickerType === Q.DATE && this.viewMode === Q.DATE ? this.dom.menu.time.style.display = "inline-block" : this.dom.menu.time.style.display = "none";
	}
	_toggleDateTimePicker() {
		this.isDatePicker ? (this.dom.dateWrap.classList.add("active"), this.dom.timeWrap.classList.remove("active"), this.dom.menu.time.innerText = this.lang.timeSelect) : (this.dom.dateWrap.classList.remove("active"), this.dom.timeWrap.classList.add("active"), this.dom.menu.time.innerText = this.lang.return, this._setTimePick());
	}
	_setDatePick(e, t, n) {
		this.now = new Date(e, t, n), this.pickDate?.setFullYear(e), this.pickDate?.setMonth(t), this.pickDate?.setDate(n), this._update();
	}
	_setTimePick(e = !0) {
		let t = this.pickDate?.getHours() || 0, n = this.pickDate?.getMinutes() || 0, r = this.pickDate?.getSeconds() || 0, { hour: i, minute: a, second: o } = this.dom.time;
		[
			i,
			a,
			o
		].forEach((e) => {
			e.querySelectorAll("li").forEach((e) => e.classList.remove("active"));
		}), [
			[i, t],
			[a, n],
			[o, r]
		].forEach(([t, n]) => {
			let r = t.querySelector(`[data-id='${n}']`);
			r.classList.add("active"), e && he(t, r);
		});
	}
	_preMonth() {
		this.now.setMonth(this.now.getMonth() - 1), this._update();
	}
	_nextMonth() {
		this.now.setMonth(this.now.getMonth() + 1), this._update();
	}
	_preYear() {
		this.now.setFullYear(this.now.getFullYear() - 1), this._update();
	}
	_nextYear() {
		this.now.setFullYear(this.now.getFullYear() + 1), this._update();
	}
	_preYearPage() {
		this.yearPageStart -= 12, this._update();
	}
	_nextYearPage() {
		this.yearPageStart += 12, this._update();
	}
	_now() {
		this.pickDate = /* @__PURE__ */ new Date(), this.now = /* @__PURE__ */ new Date(), this.datePickerType === Q.YEAR && (this.yearPageStart = this.now.getFullYear() - 5), this.dispose();
	}
	_toggleVisible(e) {
		e ? this.dom.container.classList.add("active") : this.dom.container.classList.remove("active");
	}
	_submit() {
		if (this.options.onSubmit && this.pickDate) {
			let e = this.renderOptions?.dateFormat, t = this.formatDate(this.pickDate, e);
			this.options.onSubmit(t);
		}
	}
	formatDate(e, t = "YYYY-MM-DD HH:mm:ss") {
		let n = t, r = e.getFullYear().toString(), i = (e.getMonth() + 1).toString(), a = e.getDate().toString(), o = e.getHours(), s = o % 12 == 0 ? 12 : o % 12, c = e.getMinutes().toString(), l = e.getSeconds().toString(), u = e.getMilliseconds().toString(), d = {
			"y+": r,
			"Y+": r,
			"M+": i,
			"d+": a,
			"D+": a,
			"h+": s.toString(),
			"H+": o.toString(),
			"m+": c,
			"s+": l,
			"S+": u
		};
		for (let e in d) {
			let r = RegExp("(" + e + ")").exec(t), i = e;
			r && (n = n.replace(r[1], r[1].length === 1 ? d[i] : d[i].padStart(r[1].length, "0")));
		}
		return n;
	}
	render(e) {
		this.renderOptions = e, this.lang = this._getLang(), this._setLangChange(), this._setValue(), this.datePickerType = this._getDatePickerType(e.dateFormat), this.datePickerType === Q.YEAR ? (this.viewMode = Q.YEAR, this.yearPageStart = this.now.getFullYear() - 5) : this.viewMode = this.datePickerType === Q.MONTH ? Q.MONTH : Q.DATE, this._update(), this._switchView(), this._setPosition(), this.isDatePicker = !0, this.datePickerType === Q.DATE && this._toggleDateTimePicker(), this._toggleVisible(!0);
	}
	dispose() {
		this._toggleVisible(!1);
	}
	destroy() {
		this.dom.container.remove();
	}
}, Ii = class {
	draw;
	element;
	control;
	isPopup;
	datePicker;
	options;
	constructor(e, t) {
		let n = t.getDraw();
		this.draw = n, this.options = n.getOptions(), this.element = e, this.control = t, this.isPopup = !1, this.datePicker = null;
	}
	setElement(e) {
		this.element = e;
	}
	getElement() {
		return this.element;
	}
	getIsPopup() {
		return this.isPopup;
	}
	getValue(e = {}) {
		let t = e.elementList || this.control.getElementList(), n = this.control.getValueRange(e);
		if (!n) return [];
		let r = [], { startIndex: i, endIndex: a } = n;
		for (let e = i; e <= a; e++) {
			let n = t[e];
			n.controlComponent === K.VALUE && !hn(n) && r.push(n);
		}
		return r;
	}
	setValue(e, t = {}, n = {}) {
		if (!n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return -1;
		let r = t.elementList || this.control.getElementList(), i = t.range || this.control.getRange();
		this.control.shrinkBoundary(t);
		let { startIndex: a, endIndex: o } = i, s = this.control.getDraw();
		a === o ? this.control.removePlaceholder(a, t) : s.deleteElementList(r, a + 1, o - a, { isIgnoreDeletedRule: n.isIgnoreDeletedRule });
		let c = r[a], l = c.type && !Be.includes(c.type) || c.controlComponent === K.PREFIX || c.controlComponent === K.PRE_TEXT ? V(c, [
			"control",
			"controlId",
			...Le
		]) : ae(c, ["type"]), u = i.startIndex + 1;
		for (let t = 0; t < e.length; t++) {
			let n = {
				...l,
				...e[t],
				controlComponent: K.VALUE
			};
			kn(r, [n], a, { editorOptions: this.options }), s.getTraceParticle().markElementListInserted([n]), s.spliceElementList(r, u + t, 0, [n]);
		}
		return u + e.length - 1;
	}
	clearSelect(e = {}, t = {}) {
		let { isIgnoreDisabledRule: n = !1, isAddPlaceholder: r = !0 } = t;
		if (!n && this.control.getIsDisabledControl(e)) return -1;
		let i = this.control.getValueRange(e);
		if (!i) return -1;
		let { startIndex: a, endIndex: o } = i;
		if (!~a || !~o) return -1;
		let s = e.elementList || this.control.getElementList(), c = this.control.getDraw(), l = a + 1, u = this.control.removePlaceholderInRange(s, l, o - a);
		return c.deleteElementList(s, l, u, { isIgnoreDeletedRule: t.isIgnoreDeletedRule }), r && this.control.addPlaceholder(a, e), a;
	}
	setSelect(e, t = {}, n = {}) {
		if (!n.isIgnoreDisabledRule && this.control.getIsDisabledControl(t)) return;
		let r = t.elementList || this.control.getElementList(), i = t.range || this.control.getRange(), a = this.getValue(t)[0], o = a ? V(a, Te) : V(r[i.startIndex], Le), s = this.clearSelect(t, {
			isAddPlaceholder: !1,
			isIgnoreDeletedRule: n.isIgnoreDeletedRule
		});
		if (!~s) return;
		let c = ae(r[s], Te), l = s + 1, u = this.control.getDraw();
		for (let t = 0; t < e.length; t++) {
			let n = {
				...o,
				...c,
				type: H.TEXT,
				value: e[t],
				controlComponent: K.VALUE
			};
			kn(r, [n], s, { editorOptions: this.options }), u.getTraceParticle().markElementListInserted([n]), u.spliceElementList(r, l + t, 0, [n]);
		}
		if (!t.range) {
			let n = l + e.length - 1;
			this.control.repaintControl({ curIndex: n }), this.control.emitControlContentChange({ context: t }), this.destroy();
		}
	}
	keydown(e) {
		if (this.control.getIsDisabledControl()) return null;
		let t = this.control.getElementList(), n = this.control.getRange();
		this.control.shrinkBoundary();
		let { startIndex: r, endIndex: i } = n, a = t[r], o = t[i], s = this.control.getDraw();
		if (e.key === Z.Backspace) return r === i ? a.controlComponent === K.PREFIX || a.controlComponent === K.PRE_TEXT || o.controlComponent === K.POSTFIX || o.controlComponent === K.POST_TEXT || a.controlComponent === K.PLACEHOLDER ? this.control.removeControl(r) : (s.deleteElementList(t, r, 1), this.getValue().length || this.control.addPlaceholder(r - 1), r - 1) : (s.deleteElementList(t, r + 1, i - r), this.getValue().length || this.control.addPlaceholder(r), r);
		if (e.key === Z.Delete) {
			if (r !== i) return s.deleteElementList(t, r + 1, i - r), this.getValue().length || this.control.addPlaceholder(r), r;
			{
				let e = t[i + 1];
				return (a.controlComponent === K.PREFIX || a.controlComponent === K.PRE_TEXT) && e.controlComponent === K.PLACEHOLDER || e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT || a.controlComponent === K.PLACEHOLDER ? this.control.removeControl(r) : (s.deleteElementList(t, r + 1, 1), this.getValue().length || this.control.addPlaceholder(r), r);
			}
		}
		return i;
	}
	cut() {
		if (this.control.getIsDisabledControl()) return -1;
		this.control.shrinkBoundary();
		let { startIndex: e, endIndex: t } = this.control.getRange();
		if (e === t) return e;
		let n = this.control.getDraw(), r = this.control.getElementList();
		return n.deleteElementList(r, e + 1, t - e), this.getValue().length || this.control.addPlaceholder(e), e;
	}
	awake() {
		if (this.isPopup || this.control.getIsDisabledControl() || !this.control.getIsRangeWithinControl()) return;
		let e = this.control.getPosition();
		if (!e) return;
		let t = this.draw.getElementList(), { startIndex: n } = this.control.getRange();
		if (t[n + 1]?.controlId !== this.element.controlId) return;
		this.datePicker = new Fi(this.draw, { onSubmit: this._setDate.bind(this) });
		let r = this.getValue().map((e) => e.value).join("") || "", i = this.element.control?.dateFormat;
		this.datePicker.render({
			value: r,
			position: e,
			dateFormat: i
		}), this.isPopup = !0;
	}
	destroy() {
		this.isPopup &&= (this.datePicker?.destroy(), !1);
	}
	_setDate(e) {
		e ? this.setSelect(e) : this.clearSelect(), this.destroy();
	}
}, Li = class {
	control;
	calculatorDom;
	onCalculate;
	currentExpression;
	constructor(e) {
		this.control = e.control, this.onCalculate = e.onCalculate, this.calculatorDom = null, this.currentExpression = "";
	}
	createPopup() {
		let e = this.control.getPosition();
		if (!e) return;
		let t = document.createElement("div");
		t.classList.add("ce-calculator"), t.setAttribute(_e, d.POPUP);
		let n = document.createElement("div");
		n.classList.add("ce-calculator-display"), n.textContent = "0";
		let r = document.createElement("div");
		r.classList.add("ce-calculator-buttons"), [
			[
				{
					text: "C",
					type: q.UTILITY
				},
				{
					text: "←",
					type: q.UTILITY
				},
				{
					text: "%",
					type: q.OPERATOR
				},
				{
					text: "/",
					type: q.OPERATOR
				}
			],
			[
				{
					text: "7",
					type: q.NUMBER
				},
				{
					text: "8",
					type: q.NUMBER
				},
				{
					text: "9",
					type: q.NUMBER
				},
				{
					text: "*",
					type: q.OPERATOR
				}
			],
			[
				{
					text: "4",
					type: q.NUMBER
				},
				{
					text: "5",
					type: q.NUMBER
				},
				{
					text: "6",
					type: q.NUMBER
				},
				{
					text: "-",
					type: q.OPERATOR
				}
			],
			[
				{
					text: "1",
					type: q.NUMBER
				},
				{
					text: "2",
					type: q.NUMBER
				},
				{
					text: "3",
					type: q.NUMBER
				},
				{
					text: "+",
					type: q.OPERATOR
				}
			],
			[
				{
					text: "0",
					type: q.NUMBER
				},
				{
					text: ".",
					type: q.NUMBER
				},
				{
					text: "=",
					type: q.EQUAL,
					span: 2
				}
			]
		].forEach((e) => {
			e.forEach((e) => {
				let t = document.createElement("button");
				t.classList.add("ce-calculator-button"), e.type === q.OPERATOR ? t.classList.add("operator") : e.type === q.EQUAL ? t.classList.add("equal") : e.type === q.UTILITY && t.classList.add("utility"), t.textContent = e.text, t.onclick = () => {
					let t = e.text;
					if (t === "C") this.currentExpression = "", n.textContent = "0";
					else if (t === "←") this.currentExpression = this.currentExpression.slice(0, -1), n.textContent = this.currentExpression || "0";
					else if (t === "=") {
						let e = this.calculate(this.currentExpression);
						Number.isFinite(e) ? (n.textContent = e.toString(), this.currentExpression = e.toString(), this.onCalculate(e)) : (n.textContent = "Error", this.currentExpression = "");
					} else this.currentExpression += t, n.textContent = this.currentExpression;
				}, e.span && (t.style.gridColumn = `span ${e.span}`), r.appendChild(t);
			});
		}), t.appendChild(n), t.appendChild(r);
		let { coordinate: { leftTop: [i, a] }, lineHeight: o } = e, s = this.control.getPreY();
		t.style.left = `${i + this.control.getPreX()}px`, t.style.top = `${a + s + o}px`, this.control.getContainer().appendChild(t), this.calculatorDom = t;
	}
	destroy() {
		this.calculatorDom &&= (this.calculatorDom.remove(), null);
	}
	calculate(e) {
		let t = Function("return " + e)();
		return !Number.isFinite(t) || Number.isInteger(t) ? t : parseFloat(t.toFixed(10));
	}
}, Ri = class extends Pi {
	isPopup;
	calculator;
	constructor(e, t) {
		super(e, t), this.isPopup = !1, this.calculator = null;
	}
	getIsPopup() {
		return this.isPopup;
	}
	setValue(e, t = {}, n = {}) {
		if (e.some((e) => !En(e) || w.test(e.value))) return -1;
		let r = t.elementList || this.control.getElementList(), i = t.range || this.control.getRange();
		this.control.shrinkBoundary(t);
		let a = k(e), { startIndex: o, endIndex: s } = i, c = r[o];
		if (this.control.getIsExistValueByElementListIndex(r, o)) {
			let e = o;
			for (; e > 0;) {
				let t = r[e];
				if (t.controlId !== c.controlId || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) break;
				a.unshift(t), e--;
			}
			let t = s + 1;
			for (; t < r.length;) {
				let e = r[t];
				if (e.controlId !== c.controlId || e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT) break;
				a.push(e), t++;
			}
		}
		let l = Dn(a);
		return Number.isNaN(Number(l)) || !Number.isFinite(Number(l)) ? -1 : super.setValue(e, t, n);
	}
	_setCalculatedValue(e) {
		let t = super.clearValue({}, {
			isAddPlaceholder: !1,
			isIgnoreDeletedRule: !0
		});
		if (!~t) return;
		let n = this.control.getElementList(), r = this.control.getRange(), i = this.getValue()[0], a = i ? V(i, Te) : V(n[r.startIndex], Le), o = ae(n[t], Te), s = e.toString(), c = [];
		for (let e = 0; e < s.length; e++) {
			let t = {
				...a,
				...o,
				type: H.TEXT,
				value: s[e],
				controlComponent: K.VALUE
			};
			c.push(t);
		}
		this.setValue(c), this.control.repaintControl({ curIndex: t + c.length }), this.control.emitControlContentChange(), this.destroy();
	}
	awake() {
		let e = this.element.control?.numberExclusiveOptions?.calculatorDisabled === !1;
		if (this.isPopup || !e || this.control.getIsDisabledControl() || !this.control.getIsRangeWithinControl()) return;
		let { startIndex: t } = this.control.getRange();
		this.control.getElementList()[t + 1]?.controlId === this.element.controlId && (this.calculator = new Li({
			control: this.control,
			onCalculate: (e) => {
				this._setCalculatedValue(e);
			}
		}), this.calculator.createPopup(), this.isPopup = !0);
	}
	destroy() {
		this.isPopup &&= (this.calculator?.destroy(), this.calculator = null, !1);
	}
}, zi = class {
	controlBorder;
	draw;
	range;
	listener;
	eventBus;
	controlSearch;
	options;
	controlOptions;
	activeControl;
	activeControlValue;
	preElement;
	constructor(e) {
		this.controlBorder = new Mi(e), this.draw = e, this.range = e.getRange(), this.listener = e.getListener(), this.eventBus = e.getEventBus(), this.controlSearch = new ji(this), this.options = e.getOptions(), this.controlOptions = this.options.control, this.activeControl = null, this.activeControlValue = [], this.preElement = null;
	}
	setHighlightList(e) {
		this.controlSearch.setHighlightList(e);
	}
	computeHighlightList() {
		this.controlSearch.getHighlightList().length && this.controlSearch.computeHighlightList();
	}
	renderHighlightList(e, t) {
		this.controlSearch.getHighlightMatchResult().length && this.controlSearch.renderHighlightList(e, t);
	}
	getDraw() {
		return this.draw;
	}
	filterAssistElement(e) {
		let { filterEmptyControl: t } = this.options.modeRule[p.PRINT];
		return e.filter((n, r) => {
			if (n.type === H.TABLE) {
				let e = n.trList;
				for (let t = 0; t < e.length; t++) {
					let n = e[t];
					for (let e = 0; e < n.tdList.length; e++) {
						let t = n.tdList[e];
						t.value = this.filterAssistElement(t.value);
					}
				}
			}
			if (!n.controlId) return !0;
			if (n.isControlMinWidthPlaceholder) return !1;
			if (n.control?.minWidth) {
				if (n.controlComponent === K.PREFIX || n.controlComponent === K.POSTFIX) return n.value = "", !0;
			} else {
				if (n.control?.preText && n.controlComponent === K.PRE_TEXT) {
					let t = !1, i = r + 1;
					for (; i < e.length;) {
						let r = e[i];
						if (n.controlId !== r.controlId) break;
						if (r.controlComponent === K.VALUE) {
							t = !0;
							break;
						}
						i++;
					}
					return t;
				}
				if (n.control?.postText && n.controlComponent === K.POST_TEXT) {
					let t = !1, i = r - 1;
					for (; i >= 0;) {
						let r = e[i];
						if (n.controlId !== r.controlId) break;
						if (r.controlComponent === K.VALUE) {
							t = !0;
							break;
						}
						i--;
					}
					return t;
				}
			}
			return n.controlComponent !== K.PREFIX && n.controlComponent !== K.POSTFIX && (!t || n.controlComponent !== K.PLACEHOLDER);
		});
	}
	getIsRangeCanCaptureEvent() {
		if (!this.activeControl) return !1;
		let { startIndex: e, endIndex: t } = this.getRange();
		if (!~e && !~t) return !1;
		let n = this.getElementList(), r = n[e];
		if (e === t && r.controlComponent === K.POSTFIX) return !0;
		let i = n[t], a = Wn(n, e), o = Wn(n, t);
		return !!(a && a === o && i.controlComponent !== K.POSTFIX);
	}
	getIsRangeInPostfix() {
		if (!this.activeControl) return !1;
		let { startIndex: e, endIndex: t } = this.getRange();
		return e === t && this.getElementList()[e].controlComponent === K.POSTFIX;
	}
	getIsRangeWithinControl() {
		let { startIndex: e, endIndex: t } = this.getRange();
		if (!~e && !~t) return !1;
		let n = this.getElementList(), r = n[t], i = Wn(n, e), a = Wn(n, t);
		return !!(i && i === a && r.controlComponent !== K.POSTFIX);
	}
	getIsElementListContainFullControl(e) {
		if (!e.some((e) => e.controlId)) return !1;
		let t = 0, n = 0;
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			i.controlComponent === K.PREFIX ? t++ : i.controlComponent === K.POSTFIX && n++;
		}
		return !t || !n ? !1 : t === n;
	}
	getIsDisabledControl(e = {}) {
		if (this.draw.isDesignMode() || !this.activeControl) return !1;
		let { startIndex: t, endIndex: n } = e.range || this.range.getRange();
		return t === n && ~t && ~n && (e.elementList || this.getElementList())[t].controlComponent === K.POSTFIX ? !1 : !!this.activeControl.getElement()?.control?.disabled;
	}
	getIsDisabledPasteControl(e = {}) {
		if (this.draw.isDesignMode() || !this.activeControl) return !1;
		let { startIndex: t, endIndex: n } = e.range || this.range.getRange();
		return t === n && ~t && ~n && (e.elementList || this.getElementList())[t].controlComponent === K.POSTFIX ? !1 : !!this.activeControl.getElement()?.control?.pasteDisabled;
	}
	getIsExistValueByElementListIndex(e, t) {
		let n = e[t];
		if (!n.controlId) return !1;
		if (n.control?.type === G.CHECKBOX || n.control?.type === G.RADIO) return !!n.control?.code;
		if (n.controlComponent === K.VALUE) return !0;
		if (n.controlComponent === K.PLACEHOLDER) return !1;
		if (n.controlComponent === K.PREFIX || n.controlComponent === K.PRE_TEXT) {
			let r = t;
			for (; r < e.length;) {
				let t = Un(e, r, 1, n.controlId);
				if (t < 0 || t >= e.length) return !1;
				let i = e[t];
				if (i.controlId !== n.controlId) return !1;
				if (i.controlComponent === K.VALUE) return !0;
				if (i.controlComponent === K.PLACEHOLDER) return !1;
				r = t;
			}
		}
		if (n.controlComponent === K.POSTFIX || n.controlComponent === K.POST_TEXT) {
			let r = t;
			for (; r >= 0;) {
				let t = Un(e, r, -1, n.controlId);
				if (t < 0) return !1;
				let i = e[t];
				if (i.controlId !== n.controlId) return !1;
				if (i.controlComponent === K.VALUE) return !0;
				if (i.controlComponent === K.PLACEHOLDER) return !1;
				r = t;
			}
		}
		return !1;
	}
	getControlHighlight(e, t) {
		return this.controlSearch.getControlHighlight(e, t);
	}
	getContainer() {
		return this.draw.getContainer();
	}
	getElementList() {
		return this.draw.getElementList();
	}
	getPosition() {
		let e = this.draw.getPosition().getPositionList(), { endIndex: t } = this.range.getRange();
		return e[t] || null;
	}
	getPreY() {
		let e = this.getPosition()?.pageNo ?? this.draw.getPageNo();
		return this.draw.getPageOffset(e).y;
	}
	getPreX() {
		let e = this.getPosition()?.pageNo ?? this.draw.getPageNo();
		return this.draw.getPageOffset(e).x;
	}
	getRange() {
		return this.range.getRange();
	}
	getValueRange(e = {}) {
		let t = e.elementList || this.getElementList(), { startIndex: n } = e.range || this.getRange(), r = t[n], i = n;
		for (; i > 0;) {
			let e = Un(t, i, -1, r.controlId);
			if (e < 0) break;
			let n = t[e];
			if (n.controlId !== r.controlId || n.controlComponent === K.PREFIX || n.controlComponent === K.PRE_TEXT) {
				i = e;
				break;
			}
			i = e;
		}
		let a = n;
		for (; a < t.length;) {
			let e = Un(t, a, 1, r.controlId);
			if (e < 0 || e >= t.length) break;
			let n = t[e];
			if (n.controlId !== r.controlId || n.controlComponent === K.POSTFIX || n.controlComponent === K.POST_TEXT) break;
			a = e;
		}
		return i === a ? null : {
			startIndex: i,
			endIndex: a
		};
	}
	shrinkBoundary(e = {}) {
		this.range.shrinkBoundary(e);
	}
	getActiveControl() {
		return this.activeControl;
	}
	getControlElementList(e = {}) {
		let t = e.elementList || this.getElementList(), { startIndex: n } = e.range || this.getRange(), r = t[n];
		if (!r?.controlId) return [];
		let i = [r], a = n;
		for (; a > 0;) {
			let e = Un(t, a, -1, r.controlId);
			if (e < 0) break;
			let n = t[e];
			if (n.controlId !== r.controlId) break;
			i.unshift(n), a = e;
		}
		let o = n;
		for (; o < t.length;) {
			let e = Un(t, o, 1, r.controlId);
			if (e < 0 || e >= t.length) break;
			let n = t[e];
			if (n.controlId !== r.controlId) break;
			i.push(n), o = e;
		}
		return i;
	}
	updateActiveControlValue() {
		this.activeControl && (this.activeControlValue = this.getControlElementList());
	}
	emitControlChange(e) {
		if (!this.activeControl) return;
		let t = this.eventBus.isSubscribe("controlChange");
		if (!this.listener.controlChange && !t) return;
		let n, r = this.activeControlValue, i = this.activeControl.getElement();
		r?.length ? n = X(r)[0].control : (n = xn(k(i)).control, n.value = []);
		let a = {
			state: e,
			control: n,
			controlId: i.controlId
		};
		this.listener.controlChange?.(a), t && this.eventBus.emit("controlChange", a);
	}
	initControl() {
		let e = this.getElementList()[this.getRange().startIndex];
		if (this.activeControl) {
			(this.activeControl instanceof Ni || this.activeControl instanceof Ii || this.activeControl instanceof Ri) && (e.controlComponent === K.POSTFIX ? this.activeControl.destroy() : this.activeControl.awake()), this.preElement?.controlId === e.controlId && (e.controlComponent === K.POSTFIX ? this.emitControlChange(Ot.INACTIVE) : this.preElement?.controlComponent === K.POSTFIX && this.emitControlChange(Ot.ACTIVE));
			let t = this.activeControl.getElement();
			if (e.controlId === t.controlId) {
				this.updateActiveControlValue(), this.preElement = e;
				return;
			}
		}
		if (this.destroyControl(), this.draw.isReadonly()) return;
		let t = e.control;
		if (t.type === G.TEXT) this.activeControl = new Pi(e, this);
		else if (t.type === G.SELECT) {
			let t = new Ni(e, this);
			this.activeControl = t, t.awake();
		} else if (t.type === G.CHECKBOX) this.activeControl = new sr(e, this);
		else if (t.type === G.RADIO) this.activeControl = new cr(e, this);
		else if (t.type === G.DATE) {
			let t = new Ii(e, this);
			this.activeControl = t, t.awake();
		} else if (t.type === G.NUMBER) {
			let t = new Ri(e, this);
			this.activeControl = t, t.awake();
		}
		this.updateActiveControlValue(), this.preElement = e, e.controlComponent !== K.POSTFIX && this.emitControlChange(Ot.ACTIVE);
	}
	destroyControl(e = {}) {
		if (!this.activeControl) return;
		let { isEmitEvent: t = !0 } = e;
		(this.activeControl instanceof Ni || this.activeControl instanceof Ii || this.activeControl instanceof Ri) && this.activeControl.destroy(), t && this.preElement?.controlComponent !== K.POSTFIX && this.emitControlChange(Ot.INACTIVE), this.preElement = null, this.activeControl = null, this.activeControlValue = [];
	}
	repaintControl(e = {}) {
		let { curIndex: t, isCompute: n = !0, isSubmitHistory: r = !0, isSetCursor: i = !0 } = e;
		t === void 0 ? (this.range.clearRange(), this.draw.render({
			isCompute: n,
			isSubmitHistory: r,
			isSetCursor: !1
		})) : (this.range.setRange(t, t), this.draw.render({
			curIndex: t,
			isCompute: n,
			isSetCursor: i,
			isSubmitHistory: r
		}));
	}
	emitControlContentChange(e) {
		let t = this.eventBus.isSubscribe("controlContentChange");
		if (!t && !this.listener.controlContentChange) return;
		let n = e?.controlElement || this.activeControl?.getElement();
		if (!n) return;
		let r = e?.context?.elementList || this.getElementList(), { startIndex: i } = e?.context?.range || this.getRange();
		if (!r[i]?.controlId) return;
		let a = e?.controlValue || this.getControlElementList(e?.context), o;
		if (a?.length ? o = X(a)[0].control : (o = n.control, o.value = []), !o) return;
		let s = {
			control: o,
			controlId: n.controlId
		};
		this.listener.controlContentChange?.(s), t && this.eventBus.emit("controlContentChange", s);
	}
	reAwakeControl() {
		if (!this.activeControl) return;
		let e = this.getElementList()[this.getRange().startIndex];
		this.activeControl.setElement(e), (this.activeControl instanceof Ii || this.activeControl instanceof Ni || this.activeControl instanceof Ri) && this.activeControl.getIsPopup() && (this.activeControl.destroy(), this.activeControl.awake());
	}
	selectValue() {
		let e = this.getElementList(), { startIndex: t } = this.getRange(), n = e[t];
		if (!n?.controlId || n.controlComponent !== K.VALUE && e[t + 1]?.controlComponent === K.VALUE) return !1;
		let r = t;
		for (; r > 0 && e[r].controlComponent === K.VALUE;) r--;
		let i = t + 1;
		for (; i < e.length;) {
			if (e[i].controlComponent !== K.VALUE) {
				i--;
				break;
			}
			i++;
		}
		if (r !== i) {
			let e = this.range.getRange();
			return this.range.replaceRange({
				...e,
				startIndex: r,
				endIndex: i
			}), this.draw.render({
				isCompute: !1,
				isSetCursor: !1,
				isSubmitHistory: !1
			}), !0;
		}
		return !1;
	}
	moveCursor(e) {
		let { index: t, trIndex: n, tdIndex: r, tdValueIndex: a } = e, o = this.draw.getOriginalElementList(), s, c = e.isTable ? a : t;
		e.isTable ? (o = o[t].trList[n].tdList[r].value, s = o[a]) : s = o[t];
		let l = this.draw.getTraceParticle();
		if (!this.draw.isDesignMode() && (s.hide || s.control?.hide || s.area?.hide || l.isTraceHidden(s))) {
			let e = Hn(o, c, i.BEFORE, (e) => l.isTraceHidden(e));
			return {
				newIndex: e,
				newElement: o[e]
			};
		}
		if (s.controlComponent === K.VALUE) return {
			newIndex: c,
			newElement: s
		};
		if (s.controlComponent === K.POSTFIX) {
			let e = c + 1;
			for (; e < o.length;) {
				if (o[e].controlId !== s.controlId) return {
					newIndex: e - 1,
					newElement: o[e - 1]
				};
				if (e === o.length - 1) return {
					newIndex: e,
					newElement: o[e]
				};
				e++;
			}
		} else if (s.controlComponent === K.PREFIX || s.controlComponent === K.PRE_TEXT) {
			let e = c + 1;
			for (; e < o.length;) {
				let t = o[e];
				if (t.controlId !== s.controlId || t.controlComponent !== K.PREFIX && t.controlComponent !== K.PRE_TEXT) return {
					newIndex: e - 1,
					newElement: o[e - 1]
				};
				e++;
			}
		} else if (s.controlComponent === K.PLACEHOLDER || s.controlComponent === K.POST_TEXT) {
			let e = c - 1;
			for (; e > 0;) {
				let t = o[e];
				if (t.controlId !== s.controlId || t.controlComponent === K.VALUE || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) return {
					newIndex: e,
					newElement: o[e]
				};
				e--;
			}
		}
		return {
			newIndex: c,
			newElement: s
		};
	}
	getControlStartIndex(e, t, n) {
		let r = t;
		for (; r > 0 && e[r - 1]?.controlId === n && (e[r - 1]?.controlComponent === K.PREFIX || e[r - 1]?.controlComponent === K.PRE_TEXT);) r--;
		return r;
	}
	getControlEndIndex(e, t, n) {
		let r = t;
		for (; r < e.length - 1 && e[r + 1]?.controlId === n && (e[r + 1]?.controlComponent === K.POST_TEXT || e[r + 1]?.controlComponent === K.POSTFIX);) r++;
		return r;
	}
	removeControl(e, t = {}) {
		let n = t.elementList || this.getElementList(), r = n[e];
		if (!this.draw.isDesignMode() && !r?.hide && !r?.control?.hide && !r?.area?.hide) {
			let { deletable: t = !0 } = r.control;
			if (!t) return null;
			let i = this.draw.getMode();
			if (i === p.FORM && this.options.modeRule[i].controlDeletableDisabled) return null;
			let a = r.controlId, o = e;
			for (; o < n.length;) {
				let e = n[o];
				if (e.controlId === a && e.controlComponent === K.POSTFIX) break;
				if (e.controlId !== a && e.controlComponent === K.PREFIX && e.control?.deletable === !1) return null;
				o++;
			}
		}
		let i = -1, a = -1, o = e;
		if (r.controlComponent === K.PREFIX || r.controlComponent === K.PRE_TEXT) i = this.getControlStartIndex(n, o, r.controlId) - 1;
		else for (; o > 0;) {
			let e = Un(n, o, -1, r.controlId);
			if (e < 0) break;
			let t = n[e];
			if (t.controlId !== r.controlId) {
				i = e;
				break;
			}
			if (t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) {
				i = this.getControlStartIndex(n, e, r.controlId) - 1;
				break;
			}
			o = e;
		}
		let s = e;
		if (r.controlComponent === K.POSTFIX || r.controlComponent === K.POST_TEXT) a = this.getControlEndIndex(n, s, r.controlId);
		else for (; s < n.length;) {
			let e = n[s];
			if (e.controlComponent === K.POSTFIX || e.controlComponent === K.POST_TEXT) {
				a = this.getControlEndIndex(n, s, r.controlId);
				break;
			}
			let t = Un(n, s, 1, r.controlId);
			if (t >= n.length) {
				a = t - 1;
				break;
			}
			s = t;
		}
		return s >= n.length && (a = n.length - 1), !~i && !~a ? e : (i = ~i ? i : 0, this.draw.deleteElementList(n, i + 1, a - i), i);
	}
	removePlaceholder(e, t = {}) {
		let n = t.elementList || this.getElementList(), r = n[e], i = n[e + 1];
		if (r.controlComponent === K.PLACEHOLDER || i.controlComponent === K.PLACEHOLDER) {
			let t = !1, i = e;
			for (; i < n.length;) {
				let a = n[i];
				if (a.controlId !== r.controlId) break;
				a.controlComponent === K.PLACEHOLDER ? (t || (t = !0, this.draw.getHistoryManager().popUndo(), this.draw.submitHistory(e)), n.splice(i, 1)) : i++;
			}
		}
	}
	removePlaceholderInRange(e, t, n) {
		for (let r = t + n - 1; r >= t; r--) e[r]?.controlComponent === K.PLACEHOLDER && (e.splice(r, 1), n--);
		return n;
	}
	addPlaceholder(e, t = {}) {
		let n = t.elementList || this.getElementList(), r = n[e], i = r.control;
		if (!i.placeholder) return;
		let a = N(i.placeholder), o = V(r, Le);
		for (let t = 0; t < a.length; t++) {
			let i = a[t], s = {
				...o,
				value: i === "\n" ? "​" : i,
				controlId: r.controlId,
				type: H.CONTROL,
				control: r.control,
				controlComponent: K.PLACEHOLDER,
				color: this.controlOptions.placeholderColor
			};
			kn(n, [s], e, { editorOptions: this.options }), this.draw.spliceElementList(n, e + t + 1, 0, [s]);
		}
	}
	setValue(e) {
		if (!this.activeControl) throw Error("active control is null");
		return this.activeControl.setValue(e);
	}
	setControlProperties(e, t = {}) {
		let n = t.elementList || this.getElementList(), { startIndex: r } = t.range || this.getRange(), i = n[r];
		i.control = {
			...i.control,
			...e
		};
		let a = r;
		for (; a > 0;) {
			let t = Un(n, a, -1, i.controlId);
			if (t < 0) break;
			let r = n[t];
			if (r.controlId !== i.controlId) break;
			r.control = {
				...r.control,
				...e
			}, a = t;
		}
		let o = r;
		for (; o < n.length;) {
			let t = Un(n, o, 1, i.controlId);
			if (t < 0 || t >= n.length) break;
			let r = n[t];
			if (r.controlId !== i.controlId) break;
			r.control = {
				...r.control,
				...e
			}, o = t;
		}
	}
	keydown(e) {
		if (!this.activeControl) throw Error("active control is null");
		return this.activeControl.keydown(e);
	}
	cut() {
		if (!this.activeControl) throw Error("active control is null");
		return this.activeControl.cut();
	}
	getValueById(e) {
		let { id: t, groupId: n, conceptId: r, areaId: i } = e, a = [];
		if (!t && !r && !n) return a;
		let o = (e, s) => {
			let c = 0;
			for (; c < e.length;) {
				let l = e[c];
				if (c++, l.type === H.TABLE) {
					let e = l.trList;
					for (let t = 0; t < e.length; t++) {
						let n = e[t];
						for (let e = 0; e < n.tdList.length; e++) {
							let t = n.tdList[e];
							o(t.value, s);
						}
					}
				}
				if (!l.control || n && l.control.groupId !== n || t && l.controlId !== t || r && l.control.conceptId !== r || i && l.areaId !== i) continue;
				let { type: u, code: d, valueSets: f } = l.control, p = c, m = "", h = [], g = !hn(l);
				for (; p < e.length;) {
					let t = e[p];
					if (t.controlId !== l.controlId) break;
					let n = hn(t);
					n || (g = !0), !n && (u === G.TEXT || u === G.DATE || u === G.NUMBER) && t.controlComponent === K.VALUE && (m += t.value, h.push(ae(t, Ie))), p++;
				}
				if (!g) {
					c = p;
					continue;
				}
				if (u === G.TEXT || u === G.DATE || u === G.NUMBER) a.push({
					...l.control,
					zone: s,
					value: m || null,
					innerText: m || null,
					elementList: X(h)
				});
				else if (u === G.SELECT || u === G.CHECKBOX || u === G.RADIO) {
					let e = d?.split(",").map((e) => f?.find((t) => t.code === e)?.value).filter(Boolean).join("");
					a.push({
						...l.control,
						zone: s,
						value: d || null,
						innerText: e || null
					});
				}
				c = p;
			}
		}, s = [
			{
				zone: m.HEADER,
				elementList: this.draw.getHeaderElementList()
			},
			{
				zone: m.MAIN,
				elementList: this.draw.getOriginalMainElementList()
			},
			{
				zone: m.FOOTER,
				elementList: this.draw.getFooterElementList()
			}
		];
		for (let { zone: e, elementList: t } of s) o(t, e);
		return a;
	}
	setValueListById(e) {
		if (!e.length) return;
		let t = !1, n = !1, r = (i) => {
			let a = 0;
			for (; a < i.length;) {
				let o = i[a];
				if (a++, o.type === H.TABLE) {
					let e = o.trList;
					for (let t = 0; t < e.length; t++) {
						let n = e[t];
						for (let e = 0; e < n.tdList.length; e++) {
							let t = n.tdList[e];
							r(t.value);
						}
					}
				}
				if (!o.control) continue;
				let s = e.find((e) => (!e.groupId || e.groupId === o.control?.groupId) && (e.id && o.controlId === e.id || e.conceptId && o.control.conceptId === e.conceptId || e.areaId && o.areaId === e.areaId));
				if (!s) continue;
				let { value: c, isSubmitHistory: l = !0 } = s;
				t = !0, l && (n = !0);
				let { type: u } = o.control, d = a;
				for (; d < i.length && i[d].controlId === o.controlId;) d++;
				let f = a - 1, p = -1, m = -1;
				for (let e = f; e < d; e++) {
					let t = i[e].controlComponent;
					(t === K.VALUE || t === K.PLACEHOLDER) && (p === -1 && (p = e), m = e);
				}
				let h = {
					range: p === -1 ? {
						startIndex: f,
						endIndex: f
					} : {
						startIndex: p - 1,
						endIndex: m
					},
					elementList: i
				}, g = {
					isIgnoreDisabledRule: !0,
					isIgnoreDeletedRule: !0
				};
				if (u === G.TEXT) {
					let e = Array.isArray(c) ? c : c ? [{ value: c }] : [];
					e.length && yn(e, {
						isHandleFirstElement: !1,
						editorOptions: this.options
					});
					let t = new Pi(o, this);
					this.activeControl = t, e.length ? t.setValue(e, h, g) : t.clearValue(h, g);
				} else if (u === G.SELECT) {
					if (Array.isArray(c)) continue;
					let e = new Ni(o, this);
					this.activeControl = e, c ? e.setSelect(c, h, g) : e.clearSelect(h, g);
				} else if (u === G.CHECKBOX) {
					if (Array.isArray(c)) continue;
					let e = new sr(o, this);
					this.activeControl = e;
					let t = c ? c.split(",") : [];
					e.setSelect(t, h, g);
				} else if (u === G.RADIO) {
					if (Array.isArray(c)) continue;
					let e = new cr(o, this);
					this.activeControl = e;
					let t = c ? [c] : [];
					e.setSelect(t, h, g);
				} else if (u === G.DATE) {
					let e = new Ii(o, this);
					this.activeControl = e, te(c) ? (c.length && yn(c, {
						isHandleFirstElement: !1,
						editorOptions: this.options
					}), e.setValue(c, h, g)) : ne(c) ? e.setSelect(c, h, g) : e.clearSelect(h, g);
				} else if (u === G.NUMBER) {
					let e = Array.isArray(c) ? c : c ? [{ value: c }] : [];
					e.length && yn(e, {
						isHandleFirstElement: !1,
						editorOptions: this.options
					});
					let t = new Ri(o, this);
					this.activeControl = t, e.length ? t.setValue(e, h, g) : t.clearValue(h, g);
				}
				this.emitControlContentChange({ context: h }), this.activeControl = null;
				let _ = a;
				for (; _ < i.length && i[_].controlId === o.controlId;) _++;
				a = _;
			}
		};
		this.destroyControl({ isEmitEvent: !1 });
		let i = [
			this.draw.getHeaderElementList(),
			this.draw.getOriginalMainElementList(),
			this.draw.getFooterElementList()
		];
		for (let e of i) r(e);
		t && (n || this.draw.getHistoryManager().recovery(), this.draw.render({
			isSubmitHistory: n,
			isSetCursor: !1
		}));
	}
	setExtensionListById(e) {
		if (!e.length) return;
		let t = (n) => {
			let r = 0;
			for (; r < n.length;) {
				let i = n[r];
				if (r++, i.type === H.TABLE) {
					let e = i.trList;
					for (let n = 0; n < e.length; n++) {
						let r = e[n];
						for (let e = 0; e < r.tdList.length; e++) {
							let n = r.tdList[e];
							t(n.value);
						}
					}
				}
				if (!i.control) continue;
				let a = e.find((e) => (!e.groupId || e.groupId === i.control?.groupId) && (e.id && i.controlId === e.id || e.conceptId && i.control.conceptId === e.conceptId || e.areaId && i.areaId === e.areaId));
				if (!a) continue;
				let { extension: o } = a;
				this.setControlProperties({ extension: o }, {
					elementList: n,
					range: {
						startIndex: r,
						endIndex: r
					}
				});
				let s = r;
				for (; s < n.length && n[s].controlId === i.controlId;) s++;
				r = s;
			}
		}, n = [
			this.draw.getHeaderElementList(),
			this.draw.getOriginalMainElementList(),
			this.draw.getFooterElementList()
		];
		for (let e of n) t(e);
	}
	setPropertiesListById(e) {
		if (!e.length) return;
		let t = !1, n = !1, r = (i) => {
			let a = 0;
			for (; a < i.length;) {
				let o = i[a];
				if (a++, o.type === H.TABLE) {
					let e = o.trList;
					for (let t = 0; t < e.length; t++) {
						let n = e[t];
						for (let e = 0; e < n.tdList.length; e++) {
							let t = n.tdList[e];
							r(t.value);
						}
					}
				}
				if (!o.control) continue;
				let s = e.find((e) => (!e.groupId || e.groupId === o.control?.groupId) && (e.id && o.controlId === e.id || e.conceptId && o.control.conceptId === e.conceptId || e.areaId && o.areaId === e.areaId));
				if (!s) continue;
				let { properties: c, isSubmitHistory: l = !0 } = s;
				t = !0, l && (n = !0), this.setControlProperties({
					...o.control,
					...c,
					value: o.control.value
				}, {
					elementList: i,
					range: {
						startIndex: a,
						endIndex: a
					}
				}), Le.forEach((e) => {
					let t = c[e];
					t && Reflect.set(o, e, t);
				});
				let u = a;
				for (; u < i.length && i[u].controlId === o.controlId;) u++;
				a = u;
			}
		}, i = {
			header: this.draw.getHeaderElementList(),
			main: this.draw.getOriginalMainElementList(),
			footer: this.draw.getFooterElementList()
		};
		for (let e in i) {
			let t = i[e];
			r(t);
		}
		if (t) {
			for (let e in i) {
				let t = e, n = X(i[t], {
					isClassifyArea: !0,
					extraPickAttrs: ["id"]
				});
				i[t] = n, yn(n, {
					editorOptions: this.options,
					isForceCompensation: !0
				});
			}
			this.draw.setEditorData(i), n || this.draw.getHistoryManager().recovery(), this.draw.render({
				isSubmitHistory: n,
				isSetCursor: !1
			});
		}
	}
	getList() {
		let e = [];
		function t(n) {
			for (let r = 0; r < n.length; r++) {
				let i = n[r];
				if (i.type === H.TABLE) {
					let e = i.trList;
					for (let n = 0; n < e.length; n++) {
						let r = e[n];
						for (let e = 0; e < r.tdList.length; e++) {
							let n = r.tdList[e].value;
							t(n);
						}
					}
				}
				if (i.controlId && !hn(i)) {
					let t = ae(i, [...Pe, ...Fe]);
					e.push(t);
				}
			}
		}
		let n = [
			this.draw.getHeader().getElementList(),
			this.draw.getOriginalMainElementList(),
			this.draw.getFooter().getElementList()
		];
		for (let e of n) t(e);
		return X(e, { extraPickAttrs: ["controlId"] });
	}
	recordBorderInfo(e, t, n, r) {
		this.controlBorder.recordBorderInfo(e, t, n, r);
	}
	drawBorder(e) {
		this.controlBorder.render(e);
	}
	getPreControlContext() {
		if (!this.activeControl) return null;
		let e = this.draw.getPosition().getPositionContext();
		if (!e) return null;
		let t = this.activeControl.getElement();
		function n(e, r) {
			for (let i = r; i > 0; i--) {
				let r = e[i];
				if (r.type === H.TABLE) {
					let e = r.trList || [];
					for (let t = e.length - 1; t >= 0; t--) {
						let a = e[t], o = a.tdList;
						for (let e = o.length - 1; e >= 0; e--) {
							let s = o[e], c = n(s.value, s.value.length - 1);
							if (c) return {
								positionContext: {
									isTable: !0,
									index: i,
									trIndex: t,
									tdIndex: e,
									tdId: s.id,
									trId: a.id,
									tableId: r.id
								},
								nextIndex: c.nextIndex
							};
						}
					}
				}
				if (!r.controlId || r.controlId === t.controlId) continue;
				let a = i;
				for (; a > 0;) {
					let t = e[a];
					if (t.controlComponent === K.VALUE || t.controlComponent === K.PREFIX || t.controlComponent === K.PRE_TEXT) break;
					a--;
				}
				return {
					positionContext: { isTable: !1 },
					nextIndex: a
				};
			}
			return null;
		}
		let { startIndex: r } = this.range.getRange(), i = n(this.getElementList(), r);
		if (i) return {
			positionContext: e.isTable ? e : i.positionContext,
			nextIndex: i.nextIndex
		};
		if (t.tableId) {
			let r = this.draw.getOriginalElementList(), { index: i, trIndex: a, tdIndex: o } = e, s = r[i].trList;
			for (let r = a; r >= 0; r--) {
				let i = s[r], c = i.tdList;
				for (let s = c.length - 1; s >= 0; s--) {
					if (a === r && s >= o) continue;
					let l = c[s], u = n(l.value, l.value.length - 1);
					if (u) return {
						positionContext: {
							isTable: !0,
							index: e.index,
							trIndex: r,
							tdIndex: s,
							tdId: l.id,
							trId: i.id,
							tableId: t.tableId
						},
						nextIndex: u.nextIndex
					};
				}
			}
			let c = n(r, i - 1);
			if (c) return {
				positionContext: { isTable: !1 },
				nextIndex: c.nextIndex
			};
		}
		return null;
	}
	getNextControlContext() {
		if (!this.activeControl) return null;
		let e = this.draw.getPosition().getPositionContext();
		if (!e) return null;
		let t = this.activeControl.getElement();
		function n(e, r) {
			for (let i = r; i < e.length; i++) {
				let r = e[i];
				if (r.type === H.TABLE) {
					let e = r.trList || [];
					for (let t = 0; t < e.length; t++) {
						let a = e[t], o = a.tdList;
						for (let e = 0; e < o.length; e++) {
							let s = o[e], c = n(s.value, 0);
							if (c) return {
								positionContext: {
									isTable: !0,
									index: i,
									trIndex: t,
									tdIndex: e,
									tdId: s.id,
									trId: a.id,
									tableId: r.id
								},
								nextIndex: c.nextIndex
							};
						}
					}
				}
				if (!(!r.controlId || r.controlId === t.controlId || e[i + 1]?.controlComponent === K.PREFIX || e[i + 1]?.controlComponent === K.PRE_TEXT)) return {
					positionContext: { isTable: !1 },
					nextIndex: i
				};
			}
			return null;
		}
		let { endIndex: r } = this.range.getRange(), i = n(this.getElementList(), r);
		if (i) return {
			positionContext: e.isTable ? e : i.positionContext,
			nextIndex: i.nextIndex
		};
		if (t.tableId) {
			let r = this.draw.getOriginalElementList(), { index: i, trIndex: a, tdIndex: o } = e, s = r[i].trList;
			for (let r = a; r < s.length; r++) {
				let i = s[r], c = i.tdList;
				for (let s = 0; s < c.length; s++) {
					if (a === r && s <= o) continue;
					let l = c[s], u = n(l.value, 0);
					if (u) return {
						positionContext: {
							isTable: !0,
							index: e.index,
							trIndex: r,
							tdIndex: s,
							tdId: l.id,
							trId: i.id,
							tableId: t.tableId
						},
						nextIndex: u.nextIndex
					};
				}
			}
			let c = n(r, i + 1);
			if (c) return {
				positionContext: { isTable: !1 },
				nextIndex: c.nextIndex
			};
		}
		return null;
	}
	initNextControl(e = {}) {
		let { direction: t = be.DOWN } = e, n = null;
		if (n = t === be.UP ? this.getPreControlContext() : this.getNextControlContext(), !n) return;
		let { nextIndex: r, positionContext: i } = n;
		this.draw.getPosition().setPositionContext(i), this.draw.getRange().replaceRange({
			startIndex: r,
			endIndex: r
		}), this.draw.render({
			curIndex: r,
			isCompute: !1,
			isSetCursor: !0,
			isSubmitHistory: !1
		});
	}
	setMinWidthControlInfo(e) {
		let { row: t, rowElement: n, controlRealWidth: r, availableWidth: i } = e;
		if (!n.control?.minWidth) return;
		let { scale: a } = this.options, o = n.control.minWidth * a, s = null;
		if (n.control?.minWidth && (n.control?.rowFlex === u.CENTER || n.control?.rowFlex === u.RIGHT)) {
			let e = n.metrics.width, r = t.elementList.length - 1;
			for (; r >= 0;) {
				let n = t.elementList[r];
				if (e += n.metrics.width, t.elementList[r - 1]?.controlComponent === K.PREFIX) {
					s = n;
					break;
				}
				r--;
			}
			s && e < o && (n.control.rowFlex === u.CENTER ? s.left = (o - e) / 2 : n.control.rowFlex === u.RIGHT && (s.left = o - e - n.metrics.width));
		}
		let c = o - r;
		if (c > 0) {
			let e = s?.left || 0, r = i - t.width - n.metrics.width, a = Math.min(r, c);
			n.left = a - e, t.width += a - e;
		}
	}
}, $;
(function(e) {
	e.IDENT = "IDENT", e.STRING = "STRING", e.NUMBER = "NUMBER", e.BOOLEAN = "BOOLEAN", e.NULL = "NULL", e.SELF = "SELF", e.OP = "OP", e.LPAREN = "LPAREN", e.RPAREN = "RPAREN", e.LBRACKET = "LBRACKET", e.RBRACKET = "RBRACKET", e.COMMA = "COMMA";
})($ ||= {});
var Bi = [
	"==",
	"!=",
	">=",
	"<=",
	"&&",
	"||"
], Vi = [
	">",
	"<",
	"!",
	"+",
	"*",
	"/",
	"%"
], Hi = {
	"(": $.LPAREN,
	")": $.RPAREN,
	"[": $.LBRACKET,
	"]": $.RBRACKET,
	",": $.COMMA
}, Ui = /[A-Za-z_$\u4e00-\u9fa5]/, Wi = /[A-Za-z0-9_$\u4e00-\u9fa5]/;
function Gi(e) {
	let t = [], n = 0, r = () => {
		let e = t[t.length - 1];
		return !e || e.type === $.OP || e.type === $.LPAREN || e.type === $.LBRACKET || e.type === $.COMMA;
	};
	for (; n < e.length;) {
		let i = e[n];
		if (i === " " || i === "	" || i === "\n" || i === "\r") {
			n++;
			continue;
		}
		let a = Hi[i];
		if (a) {
			t.push({
				type: a,
				value: i
			}), n++;
			continue;
		}
		if (i === "'" || i === "\"") {
			let r = n + 1, a = "";
			for (; r < e.length && e[r] !== i;) {
				if (e[r] === "\\" && r + 1 < e.length) {
					a += e[r + 1], r += 2;
					continue;
				}
				a += e[r], r++;
			}
			if (r >= e.length) throw Error(`表达式字符串未闭合: ${e}`);
			t.push({
				type: $.STRING,
				value: a
			}), n = r + 1;
			continue;
		}
		let o = i === "-" && /\d/.test(e[n + 1] || "") && r();
		if (/\d/.test(i) || o) {
			let r = o ? n + 1 : n;
			for (; r < e.length && /[\d.]/.test(e[r]);) r++;
			t.push({
				type: $.NUMBER,
				value: e.slice(n, r)
			}), n = r;
			continue;
		}
		if (i === "-") {
			t.push({
				type: $.OP,
				value: i
			}), n++;
			continue;
		}
		if (i === "@") {
			let r = n + 1;
			for (; r < e.length && Wi.test(e[r]);) r++;
			let i = e.slice(n + 1, r);
			if (i !== "self") throw Error(`表达式未知保留字 "@${i}"，当前仅支持 @self`);
			t.push({
				type: $.SELF,
				value: i
			}), n = r;
			continue;
		}
		let s = e.slice(n, n + 2);
		if (Bi.includes(s)) {
			t.push({
				type: $.OP,
				value: s
			}), n += 2;
			continue;
		}
		if (Vi.includes(i)) {
			t.push({
				type: $.OP,
				value: i
			}), n++;
			continue;
		}
		if (i === "=" || i === "&" || i === "|") throw Error(`表达式非法运算符 "${i}"，请使用 == / && / ||`);
		if (Ui.test(i)) {
			let r = n;
			for (; r < e.length && Wi.test(e[r]);) r++;
			let i = e.slice(n, r);
			i === "true" || i === "false" ? t.push({
				type: $.BOOLEAN,
				value: i
			}) : i === "null" ? t.push({
				type: $.NULL,
				value: i
			}) : t.push({
				type: $.IDENT,
				value: i
			}), n = r;
			continue;
		}
		throw Error(`表达式无法识别的字符 "${i}"`);
	}
	return t;
}
//#endregion
//#region src/editor/core/cascade/expression/parser.ts
var Ki = [
	"==",
	"!=",
	">",
	">=",
	"<",
	"<="
], qi = ["+", "-"], Ji = [
	"*",
	"/",
	"%"
];
function Yi(e) {
	let t = 0, n = () => e[t], r = () => e[t++], i = (e, t) => {
		let n = r();
		if (!n || n.type !== e || t && n.value !== t) throw Error(`表达式语法错误：期望 ${t || e}`);
		return n;
	}, a = () => o(), o = () => {
		let e = s();
		for (; n()?.type === $.OP && n().value === "||";) r(), e = {
			type: "logical",
			op: "||",
			left: e,
			right: s()
		};
		return e;
	}, s = () => {
		let e = c();
		for (; n()?.type === $.OP && n().value === "&&";) r(), e = {
			type: "logical",
			op: "&&",
			left: e,
			right: c()
		};
		return e;
	}, c = () => n()?.type === $.OP && n().value === "!" ? (r(), {
		type: "not",
		argument: c()
	}) : l(), l = () => {
		let e = u(), t = n();
		return t?.type === $.OP && Ki.includes(t.value) || t?.type === $.IDENT && t.value === "in" ? (r(), {
			type: "compare",
			op: t.value,
			left: e,
			right: u()
		}) : e;
	}, u = () => {
		let e = d();
		for (; n()?.type === $.OP && qi.includes(n().value);) e = {
			type: "arithmetic",
			op: r().value,
			left: e,
			right: d()
		};
		return e;
	}, d = () => {
		let e = f();
		for (; n()?.type === $.OP && Ji.includes(n().value);) e = {
			type: "arithmetic",
			op: r().value,
			left: e,
			right: f()
		};
		return e;
	}, f = () => {
		let e = n();
		if (!e) throw Error("表达式意外结束");
		if (e.type === $.SELF) throw Error("@self 仅可作为 getValue(@self) 的参数使用");
		if (e.type === $.STRING) return r(), {
			type: "literal",
			value: e.value
		};
		if (e.type === $.NUMBER) return r(), {
			type: "literal",
			value: Number(e.value)
		};
		if (e.type === $.BOOLEAN) return r(), {
			type: "literal",
			value: e.value === "true"
		};
		if (e.type === $.NULL) return r(), {
			type: "literal",
			value: null
		};
		if (e.type === $.LBRACKET) {
			r();
			let e = [];
			if (n()?.type !== $.RBRACKET) do
				e.push(f());
			while (n()?.type === $.COMMA && (r(), !0));
			return i($.RBRACKET), {
				type: "literal",
				value: e
			};
		}
		if (e.type === $.LPAREN) {
			r();
			let e = a();
			return i($.RPAREN), e;
		}
		if (e.type === $.IDENT) {
			if (r(), n()?.type === $.LPAREN) {
				if (r(), e.value === "getValue") {
					let e = r();
					if (!e) throw Error("getValue 缺少参数");
					let t;
					if (e.type === $.STRING) t = {
						kind: "id",
						value: e.value
					};
					else if (e.type === $.SELF) t = { kind: "self" };
					else throw Error("getValue 参数必须是控件 id 字符串或 @self");
					return i($.RPAREN), {
						type: "getValue",
						target: t
					};
				}
				let t = [];
				if (n()?.type !== $.RPAREN) do
					t.push(a());
				while (n()?.type === $.COMMA && (r(), !0));
				return i($.RPAREN), {
					type: "call",
					name: e.value,
					args: t
				};
			}
			throw Error(`标识符 "${e.value}" 不能直接引用，请使用 getValue('${e.value}') 获取控件值`);
		}
		throw Error(`表达式语法错误：意外的 "${e.value}"`);
	}, p = a();
	if (t < e.length) throw Error(`表达式存在多余内容: "${e[t].value}"`);
	return p;
}
//#endregion
//#region src/editor/core/cascade/expression/evaluator.ts
var Xi = /^\d{4}-\d{2}-\d{2}/;
function Zi(e) {
	return e.codes ? e.codes.length === 0 : e.code === void 0 ? !e.text || !e.text.trim() : !e.code;
}
function Qi(e) {
	return e.kind === "resolved" ? !Zi(e.value) : !!e.value;
}
function $i(e) {
	if (e.kind === "plain") {
		let t = e.value;
		return t == null ? null : typeof t == "number" || typeof t == "string" ? t : typeof t == "boolean" ? t ? "true" : "false" : String(t);
	}
	let t = e.value;
	return t.codes ? t.codes.join(",") : t.code === void 0 ? t.text ?? null : t.code;
}
function ea(e) {
	if (e === null) return null;
	if (e === "today") {
		let e = /* @__PURE__ */ new Date();
		return new Date(e.getFullYear(), e.getMonth(), e.getDate()).getTime();
	}
	if (typeof e == "string" && Xi.test(e)) {
		let t = new Date(e).getTime();
		return Number.isNaN(t) ? null : t;
	}
	return null;
}
function ta(e, t, n) {
	if (e === "in") {
		let e = n.kind === "plain" ? n.value : null;
		if (!Array.isArray(e)) return !1;
		if (t.kind === "resolved" && t.value.codes) return t.value.codes.some((t) => e.some((e) => String(e) === t));
		let r = $i(t);
		return e.some((e) => String(e) === String(r));
	}
	let r = $i(t), i = $i(n);
	if (e === "==") return String(r) === String(i);
	if (e === "!=") return String(r) !== String(i);
	if (r === null || i === null) return !1;
	if (t.kind === "resolved" && t.value.isDate || i === "today" || typeof i == "string" && Xi.test(i)) {
		let t = ea(r), n = typeof i == "number" && Number.isFinite(i) ? i : ea(i);
		return t === null || n === null ? !1 : na(e, t, n);
	}
	let a = Number(r), o = Number(i), s = String(r).trim() !== "" && Number.isFinite(a), c = String(i).trim() !== "" && Number.isFinite(o);
	if (s && c) return na(e, a, o);
	if (s || c) return !1;
	let l = String(r), u = String(i);
	switch (e) {
		case ">": return l > u;
		case ">=": return l >= u;
		case "<": return l < u;
		case "<=": return l <= u;
		default: return !1;
	}
}
function na(e, t, n) {
	switch (e) {
		case ">": return t > n;
		case ">=": return t >= n;
		case "<": return t < n;
		case "<=": return t <= n;
		default: return !1;
	}
}
function ra(e, t, n) {
	if (t === null || n === null) return null;
	if (e === "+") {
		let e = String(t), r = String(n), i = Number(t), a = Number(n);
		return e.trim() !== "" && r.trim() !== "" && Number.isFinite(i) && Number.isFinite(a) ? i + a : e + r;
	}
	let r = Number(t), i = Number(n);
	if (!Number.isFinite(r) || !Number.isFinite(i)) return null;
	switch (e) {
		case "-": return r - i;
		case "*": return r * i;
		case "/": return i === 0 ? null : r / i;
		case "%": return i === 0 ? null : r % i;
		default: return null;
	}
}
function ia(e, t) {
	let n = (e) => {
		let n = t[e];
		if (n?.kind === "resolved") return n.value;
		let r = n ? $i(n) : null;
		return { text: r === null ? null : String(r) };
	};
	switch (e) {
		case "empty": return {
			kind: "plain",
			value: Zi(n(0))
		};
		case "notEmpty": return {
			kind: "plain",
			value: !Zi(n(0))
		};
		case "len": return {
			kind: "plain",
			value: (n(0).text ?? "").length
		};
		case "count": return {
			kind: "plain",
			value: n(0).codes?.length ?? 0
		};
		case "contains": {
			let e = n(0), r = $i(t[1]);
			return r === null ? {
				kind: "plain",
				value: !1
			} : e.codes ? {
				kind: "plain",
				value: e.codes.includes(String(r))
			} : {
				kind: "plain",
				value: (e.text ?? "").includes(String(r))
			};
		}
		case "round": {
			let e = $i(t[0]);
			if (e === null) return {
				kind: "plain",
				value: null
			};
			let n = Number(e);
			if (!Number.isFinite(n)) return {
				kind: "plain",
				value: null
			};
			let r = t[1] ? Number($i(t[1])) : 0, i = 10 ** (Number.isFinite(r) ? r : 0);
			return {
				kind: "plain",
				value: Math.round(n * i) / i
			};
		}
		case "floor":
		case "ceil":
		case "abs": {
			let n = $i(t[0]);
			if (n === null) return {
				kind: "plain",
				value: null
			};
			let r = Number(n);
			return Number.isFinite(r) ? {
				kind: "plain",
				value: e === "floor" ? Math.floor(r) : e === "ceil" ? Math.ceil(r) : Math.abs(r)
			} : {
				kind: "plain",
				value: null
			};
		}
		case "min":
		case "max": {
			let n = t.map((e) => Number($i(e))).filter((e) => Number.isFinite(e));
			return n.length ? {
				kind: "plain",
				value: e === "min" ? Math.min(...n) : Math.max(...n)
			} : {
				kind: "plain",
				value: null
			};
		}
		case "power": {
			let e = $i(t[0]), n = t[1] ? $i(t[1]) : null;
			if (e === null || n === null) return {
				kind: "plain",
				value: null
			};
			let r = Number(e), i = Number(n);
			return !Number.isFinite(r) || !Number.isFinite(i) ? {
				kind: "plain",
				value: null
			} : {
				kind: "plain",
				value: r ** +i
			};
		}
		case "sqrt": {
			let e = $i(t[0]);
			if (e === null) return {
				kind: "plain",
				value: null
			};
			let n = Number(e);
			return !Number.isFinite(n) || n < 0 ? {
				kind: "plain",
				value: null
			} : {
				kind: "plain",
				value: Math.sqrt(n)
			};
		}
		case "now": return {
			kind: "plain",
			value: Date.now()
		};
		case "datediff": {
			let e = ea($i(t[0])), n = ea($i(t[1]));
			if (e === null || n === null) return {
				kind: "plain",
				value: null
			};
			let r = t[2] ? String($i(t[2])) : "d", i = r === "h" ? 36e5 : r === "m" ? 6e4 : r === "s" ? 1e3 : 864e5;
			return {
				kind: "plain",
				value: (e - n) / i
			};
		}
		default: throw Error(`未知函数: ${e}`);
	}
}
function aa(e, t) {
	switch (e.type) {
		case "literal": return Array.isArray(e.value) ? {
			kind: "plain",
			value: e.value.map((e) => $i(aa(e, t)))
		} : {
			kind: "plain",
			value: e.value
		};
		case "getValue": return {
			kind: "resolved",
			value: (e.target.kind === "self" ? t.resolveSelf?.() : t.resolve(e.target.value)) ?? { text: null }
		};
		case "logical": return e.op === "&&" ? {
			kind: "plain",
			value: Qi(aa(e.left, t)) && Qi(aa(e.right, t))
		} : {
			kind: "plain",
			value: Qi(aa(e.left, t)) || Qi(aa(e.right, t))
		};
		case "not": return {
			kind: "plain",
			value: !Qi(aa(e.argument, t))
		};
		case "compare": return {
			kind: "plain",
			value: ta(e.op, aa(e.left, t), aa(e.right, t))
		};
		case "arithmetic": return {
			kind: "plain",
			value: ra(e.op, $i(aa(e.left, t)), $i(aa(e.right, t)))
		};
		case "call":
			if (e.name === "if") {
				let n = e.args[0], r = n ? Qi(aa(n, t)) : !1, i = e.args[r ? 1 : 2];
				return i ? aa(i, t) : {
					kind: "plain",
					value: null
				};
			}
			return ia(e.name, e.args.map((e) => aa(e, t)));
	}
}
function oa(e, t) {
	return Qi(aa(e, t));
}
function sa(e, t) {
	return $i(aa(e, t));
}
//#endregion
//#region src/editor/core/cascade/CascadeManager.ts
function ca(e) {
	return typeof e == "string" ? e : String(Number.isInteger(e) ? e : parseFloat(e.toPrecision(12)));
}
var la = 10, ua = [
	"hide",
	"required",
	"disabled",
	"deletable"
], da = class {
	draw;
	control;
	eventBus;
	baselines;
	controlBaselines;
	valueCache;
	isExecuting;
	needsRerun;
	constructor(e) {
		this.draw = e, this.control = e.getControl(), this.eventBus = e.getEventBus(), this.baselines = /* @__PURE__ */ new WeakMap(), this.controlBaselines = /* @__PURE__ */ new Map(), this.valueCache = /* @__PURE__ */ new Map(), this.isExecuting = !1, this.needsRerun = !1, this.eventBus.on("contentChange", () => {
			this.executeAll();
		});
	}
	getZoneElementLists() {
		return [
			this.draw.getHeaderElementList(),
			this.draw.getOriginalMainElementList(),
			this.draw.getFooterElementList()
		];
	}
	collectAll() {
		let e = [], t = [], n = {
			byControlId: /* @__PURE__ */ new Map(),
			byConceptId: /* @__PURE__ */ new Map()
		}, r = /* @__PURE__ */ new Set(), i = (a) => {
			for (let o of a) {
				if (o.type === H.TABLE) {
					for (let e of o.trList || []) for (let t of e.tdList) i(t.value);
					continue;
				}
				let a = o.control;
				if (a) {
					if (o.controlId) {
						let e = n.byControlId.get(o.controlId);
						e ? e.push(o) : n.byControlId.set(o.controlId, [o]);
					}
					if (a.conceptId) {
						let e = n.byConceptId.get(a.conceptId);
						e ? e.push(o) : n.byConceptId.set(a.conceptId, [o]);
					}
					if (!r.has(a)) {
						if (r.add(a), a.cascade?.length) for (let t of a.cascade) {
							let n = null;
							try {
								n = Yi(Gi(t.expression));
							} catch (e) {
								console.warn(`[cascade] 表达式解析失败: ${t.expression}`, e);
							}
							e.push({
								rule: t,
								ast: n,
								hostControlId: o.controlId
							});
						}
						if (a.compute && o.controlId) {
							let e = null;
							try {
								e = Yi(Gi(a.compute));
							} catch (e) {
								console.warn(`[cascade] 计算表达式解析失败: ${a.compute}`, e);
							}
							t.push({
								controlId: o.controlId,
								expression: a.compute,
								ast: e
							});
						}
					}
				}
			}
		};
		return this.getZoneElementLists().forEach(i), {
			rules: e,
			computes: t,
			index: n
		};
	}
	resolveIdentifier = (e) => {
		if (this.valueCache.has(e)) return this.valueCache.get(e);
		let t = this.resolveIdentifierUncached(e);
		return this.valueCache.set(e, t), t;
	};
	resolveIdentifierUncached(e) {
		let t = this.control.getValueById({ id: e });
		return t.length || (t = this.control.getValueById({ conceptId: e })), this.normalizeGetValueResult(t);
	}
	resolveByControlId(e) {
		if (e) return this.normalizeGetValueResult(this.control.getValueById({ id: e }));
	}
	normalizeGetValueResult(e) {
		if (!e.length) return;
		let t = e.find((e) => e.value != null) || e[0], n = t.type;
		return n === G.SELECT || n === G.RADIO ? { code: t.value } : n === G.CHECKBOX ? { codes: t.value ? t.value.split(",") : [] } : {
			text: t.value,
			isDate: n === G.DATE
		};
	}
	findTitleRangeElements(e) {
		let t = [], n = (r) => {
			let i = 0;
			for (; i < r.length;) {
				let a = r[i];
				if (i++, a.type === H.TABLE) {
					for (let e of a.trList || []) for (let t of e.tdList) n(t.value);
					continue;
				}
				if (a.title?.conceptId !== e) continue;
				t.push(a);
				let o = i;
				for (; o < r.length;) {
					let e = r[o];
					if (a.titleId === e.titleId) {
						t.push(e), o++;
						continue;
					}
					if (e.level && wt[e.level] <= wt[a.level]) break;
					t.push(e), o++;
				}
				i = o;
			}
		};
		return this.getZoneElementLists().forEach(n), t;
	}
	recordBaseline(e, t, n) {
		let r = this.baselines.get(e);
		r || (r = {}, this.baselines.set(e, r)), t in r || (r[t] = n());
	}
	writeWithBaseline(e, t, n, r, i) {
		return this.recordBaseline(e, t, n), n() !== i && (r(i), !0);
	}
	restoreBaseline(e, t) {
		let n = this.baselines.get(e);
		if (!n || !(t in n)) return !1;
		let r = n[t];
		if (t === "elementHide") {
			if (e.hide === r) return !1;
			e.hide = r;
		} else {
			if (e.control?.[t] === r) return !1;
			let n = e.control;
			n && (n[t] = r);
		}
		return !0;
	}
	recordControlBaseline(e, t) {
		let n = e.controlId;
		if (!n) return;
		let r = this.controlBaselines.get(n);
		r || (r = {}, this.controlBaselines.set(n, r)), t in r || (r[t] = e.control?.[t]);
	}
	restoreControlBaseline(e, t) {
		let n = this.controlBaselines.get(e.controlId);
		if (!n || !(t in n)) return !1;
		let r = n[t];
		if (e.control?.[t] === r) return !1;
		let i = e.control;
		return i && (i[t] = r), !0;
	}
	applyAction(e, t, n) {
		let r = t ? e.effects : null, i = [];
		if (e.controlId) {
			let t = n.byControlId.get(e.controlId);
			t?.length && i.push(...t);
		}
		if (e.conceptId) {
			let t = n.byConceptId.get(e.conceptId);
			t?.length && i.push(...t);
		}
		let a = e.targetType || (i.length ? "control" : "title"), o = !1;
		if (a === "control") {
			let e = i;
			if (t && r) {
				let t = /* @__PURE__ */ new Set();
				for (let n of e) {
					let e = n.control;
					if (!e) continue;
					let i = !t.has(e);
					for (let t of ua) t in r && (this.recordControlBaseline(n, t), i && e[t] !== r[t] && (e[t] = r[t], o = !0));
					t.add(e);
				}
			} else for (let t of e) for (let e of ua) o = this.restoreControlBaseline(t, e) || o;
		} else {
			let n = this.findTitleRangeElements(e.conceptId || "");
			for (let e of n) o = t && r && "hide" in r ? this.writeWithBaseline(e, "elementHide", () => e.hide, (t) => {
				e.hide = t;
			}, r.hide) || o : this.restoreBaseline(e, "elementHide") || o;
		}
		return o;
	}
	applyComputes(e) {
		let t = [];
		for (let n of e) {
			if (!n.ast) continue;
			let e = null;
			try {
				e = sa(n.ast, {
					resolve: this.resolveIdentifier,
					resolveSelf: () => this.resolveByControlId(n.controlId)
				});
			} catch (e) {
				console.warn(`[cascade] 计算表达式求值失败: ${n.expression}`, e);
				continue;
			}
			let r = e === null ? null : ca(e);
			(this.control.getValueById({ id: n.controlId })[0]?.value ?? null) !== r && t.push({
				id: n.controlId,
				value: r
			});
		}
		return t.length ? (this.control.setValueListById(t), this.draw.getHistoryManager().popUndo(), !0) : !1;
	}
	executeAll() {
		if (this.isExecuting) {
			this.needsRerun = !0;
			return;
		}
		this.isExecuting = !0;
		try {
			let e = 0;
			do
				this.needsRerun = !1, this.executePass(), e++;
			while (this.needsRerun && e < la);
			this.needsRerun && console.warn("[cascade] 级联执行超过最大迭代次数，可能存在循环计算");
		} finally {
			this.isExecuting = !1, this.needsRerun = !1;
		}
	}
	executePass() {
		let { rules: e, computes: t, index: n } = this.collectAll();
		if (!e.length && !t.length) return;
		this.valueCache.clear();
		let r = this.applyComputes(t);
		r && (this.needsRerun = !0);
		for (let { rule: t, ast: i, hostControlId: a } of e) {
			let e = !1;
			if (i) try {
				e = oa(i, {
					resolve: this.resolveIdentifier,
					resolveSelf: () => this.resolveByControlId(a)
				});
			} catch (e) {
				console.warn(`[cascade] 表达式求值失败: ${t.expression}`, e);
			}
			let o = e ? t.actions : t.elseActions || null;
			if (o) for (let e of o) r = this.applyAction(e, !0, n) || r;
			else for (let e of t.actions) r = this.applyAction(e, !1, n) || r;
		}
		if (r) {
			let e = !!this.draw.getPosition().getCursorPosition();
			this.draw.render({
				isSubmitHistory: !1,
				isSetCursor: e,
				curIndex: e ? this.draw.getRange().getRange().startIndex : void 0
			});
		}
	}
}, fa = class {
	draw;
	control;
	i18n;
	highlightedControlIds;
	lastErrorBackgroundColor;
	constructor(e) {
		this.draw = e, this.control = e.getControl(), this.i18n = e.getI18n(), this.highlightedControlIds = /* @__PURE__ */ new Set(), this.lastErrorBackgroundColor = "";
	}
	collectControlElements(e) {
		let t = [];
		(!e || e === m.HEADER) && t.push(this.draw.getHeaderElementList()), (!e || e === m.MAIN) && t.push(this.draw.getOriginalMainElementList()), (!e || e === m.FOOTER) && t.push(this.draw.getFooterElementList());
		let n = [], r = /* @__PURE__ */ new Set(), i = (e) => {
			for (let t of e) {
				if (t.type === H.TABLE) {
					for (let e of t.trList || []) for (let t of e.tdList) i(t.value);
					continue;
				}
				let e = t.control;
				!e || r.has(e) || (r.add(e), n.push(t));
			}
		};
		return t.forEach(i), n;
	}
	getNormalizedValue(e) {
		let t = e.control.type, n = this.control.getValueById({ id: e.controlId }), r = (n.find((e) => e.value != null) || n[0])?.value ?? null;
		return t === G.SELECT || t === G.RADIO ? { code: r || null } : t === G.CHECKBOX ? { codes: r ? r.split(",") : [] } : {
			text: r,
			isDate: t === G.DATE
		};
	}
	isHidden(e) {
		return !!(e.control?.hide || e.hide);
	}
	t(e, t) {
		let n = this.i18n.t(e);
		if (t) for (let e in t) n = n.replace(`{${e}}`, String(t[e]));
		return n;
	}
	validateControl(e, t) {
		let n = e.control, r = this.getNormalizedValue(e), i = n.validation;
		if (n.required && (r.codes ? !r.codes.length : r.code === void 0 ? !r.text?.trim() : !r.code)) {
			t.push(i?.message || this.t("validate.required"));
			return;
		}
		if (!i) return;
		let a = "text" in r && r.text || "", o = i.message;
		if (n.type === G.TEXT && a && (i.minLength != null && a.length < i.minLength && t.push(o || this.t("validate.minLength", { min: i.minLength })), i.maxLength != null && a.length > i.maxLength && t.push(o || this.t("validate.maxLength", { max: i.maxLength })), i.pattern && !new RegExp(i.pattern).test(a) && t.push(o || this.t("validate.pattern"))), n.type === G.NUMBER && a) {
			let e = Number(a);
			Number.isFinite(e) ? (i.min != null && e < i.min && t.push(o || this.t("validate.min", { min: i.min })), i.max != null && e > i.max && t.push(o || this.t("validate.max", { max: i.max })), i.integer && !Number.isInteger(e) && t.push(o || this.t("validate.integer")), i.precision != null && (a.split(".")[1]?.length || 0) > i.precision && t.push(o || this.t("validate.precision", { precision: i.precision }))) : t.push(o || this.t("validate.invalidNumber"));
		}
		if (n.type === G.DATE && a) {
			let e = (e) => e === "today" ? new Date((/* @__PURE__ */ new Date()).toDateString()).getTime() : new Date(e).getTime(), n = e(a);
			i.minDate && n < e(i.minDate) && t.push(o || this.t("validate.minDate", { date: i.minDate })), i.maxDate && n > e(i.maxDate) && t.push(o || this.t("validate.maxDate", { date: i.maxDate }));
		}
		if (n.type === G.CHECKBOX && r.codes) {
			let e = r.codes.length;
			i.minChecked != null && e < i.minChecked && t.push(o || this.t("validate.minChecked", { count: i.minChecked })), i.maxChecked != null && e > i.maxChecked && t.push(o || this.t("validate.maxChecked", { count: i.maxChecked }));
		}
	}
	walkAllControlElements(e) {
		let t = (n) => {
			for (let r of n) {
				if (r.type === H.TABLE) {
					for (let e of r.trList || []) for (let n of e.tdList) t(n.value);
					continue;
				}
				r.controlId && e(r);
			}
		};
		t(this.draw.getHeaderElementList()), t(this.draw.getOriginalMainElementList()), t(this.draw.getFooterElementList());
	}
	applyHighlight(e) {
		this.walkAllControlElements((t) => {
			this.highlightedControlIds.has(t.controlId) && (t.highlight = e);
		}), this.draw.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		});
	}
	clearHighlight() {
		this.highlightedControlIds.size && (this.walkAllControlElements((e) => {
			this.highlightedControlIds.has(e.controlId) && e.highlight === this.lastErrorBackgroundColor && delete e.highlight;
		}), this.highlightedControlIds.clear(), this.draw.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		}));
	}
	execute(e) {
		this.draw.getCascadeManager().executeAll(), this.clearHighlight();
		let t = e?.errorBackgroundColor || this.draw.getOptions().control.errorBackgroundColor, n = [], r = this.collectControlElements(e?.zone);
		for (let e of r) {
			if (!e.control || !e.controlId || this.isHidden(e)) continue;
			let t = [];
			this.validateControl(e, t), t.length && (n.push({
				controlId: e.controlId,
				conceptId: e.control.conceptId,
				control: { ...e.control },
				errors: t
			}), this.highlightedControlIds.add(e.controlId));
		}
		return this.lastErrorBackgroundColor = t, this.highlightedControlIds.size && this.applyHighlight(t), n;
	}
}, pa = class {
	draw;
	options;
	constructor(e) {
		this.draw = e, this.options = e.getOptions();
	}
	setSelect(e) {
		let { checkbox: t } = e;
		t ? t.value = !t.value : e.checkbox = { value: !0 }, this.draw.render({
			isCompute: !1,
			isSetCursor: !1
		});
	}
	render(e) {
		let { ctx: t, x: n, index: r, row: i } = e, { y: a } = e, { checkbox: { gap: o, lineWidth: s, fillStyle: c, strokeStyle: l, checkFillStyle: u, checkStrokeStyle: d, checkMarkColor: f, verticalAlign: p }, scale: m } = this.options, { metrics: h, checkbox: g } = i.elementList[r];
		if (p === Y.TOP || p === Y.MIDDLE) {
			let e = r + 1, t = null;
			for (; e < i.elementList.length && (t = i.elementList[e], t.value === "​" || t.value === " ");) e++;
			if (t) {
				let { metrics: { boundingBoxAscent: e, boundingBoxDescent: n } } = t, r = e + n;
				r > h.height && (p === Y.TOP ? a -= e - h.height : p === Y.MIDDLE && (a -= (r - h.height) / 2));
			}
		}
		let _ = Math.round(n + o * m), v = Math.round(a - h.height + s), y = h.width - o * 2 * m, b = h.height;
		t.save(), t.beginPath(), t.translate(.5, .5), g?.value ? (t.fillStyle = u, t.fillRect(_, v, y, b), t.beginPath(), t.lineWidth = s, t.strokeStyle = d, t.rect(_, v, y, b), t.stroke(), t.beginPath(), t.strokeStyle = f, t.lineWidth = s * 2 * m, t.moveTo(_ + 2 * m, v + b / 2), t.lineTo(_ + y / 2, v + b - 3 * m), t.lineTo(_ + y - 2 * m, v + 3 * m), t.stroke()) : (t.fillStyle = c, t.fillRect(_, v, y, b), t.beginPath(), t.lineWidth = s, t.strokeStyle = l, t.rect(_, v, y, b), t.stroke()), t.closePath(), t.restore();
	}
}, ma = class {
	draw;
	options;
	constructor(e) {
		this.draw = e, this.options = e.getOptions();
	}
	setSelect(e) {
		let { radio: t } = e;
		t ? t.value = !t.value : e.radio = { value: !0 }, this.draw.render({
			isCompute: !1,
			isSetCursor: !1
		});
	}
	render(e) {
		let { ctx: t, x: n, index: r, row: i } = e, { y: a } = e, { radio: { gap: o, lineWidth: s, fillStyle: c, strokeStyle: l, verticalAlign: u }, scale: d } = this.options, { metrics: f, radio: p } = i.elementList[r];
		if (u === Y.TOP || u === Y.MIDDLE) {
			let e = r + 1, t = null;
			for (; e < i.elementList.length && (t = i.elementList[e], t.value === "​" || t.value === " ");) e++;
			if (t) {
				let { metrics: { boundingBoxAscent: e, boundingBoxDescent: n } } = t, r = e + n;
				r > f.height && (u === Y.TOP ? a -= e - f.height : u === Y.MIDDLE && (a -= (r - f.height) / 2));
			}
		}
		let m = Math.round(n + o * d), h = Math.round(a - f.height + s), g = f.width - o * 2 * d, _ = f.height;
		t.save(), t.beginPath(), t.translate(.5, .5), t.strokeStyle = p?.value ? c : l, t.lineWidth = s, t.arc(m + g / 2, h + _ / 2, g / 2, 0, Math.PI * 2), t.stroke(), p?.value && (t.beginPath(), t.fillStyle = c, t.arc(m + g / 2, h + _ / 2, g / 3, 0, Math.PI * 2), t.fill()), t.closePath(), t.restore();
	}
};
//#endregion
//#region src/editor/utils/table.ts
function ha(e) {
	return e.reduce((e, t) => e + t.width, 0);
}
function ga(e, t, n) {
	let r = ha(e);
	for (; r > t;) {
		let i = e.filter((e) => e.width > n);
		if (!i.length) return;
		let a = ha(i), o = t - (r - a);
		if (o <= 0) {
			i.forEach((e) => e.width = n);
			return;
		}
		let s = o / a;
		i.forEach((e) => {
			e.width = Math.max(n, e.width * s);
		});
		let c = ha(e);
		if (c >= r) return;
		r = c;
	}
}
function _a(e, t) {
	let n = ha(e);
	if (!n || n === t) return;
	let r = t / n;
	for (let t = 0; t < e.length; t++) e[t].width *= r;
}
//#endregion
//#region src/editor/core/worker/works/wordCount.ts?worker&inline
var va = "(function(){let e=function(e){return e.INSERTED=`inserted`,e.DELETED=`deleted`,e}({});function t(n){let r=``,i=0;for(;i<n.length;){let a=n[i],o=a.trace;if(o?.length&&o[o.length-1].type===e.DELETED){i++;continue}if(a.type===`table`){if(a.trList)for(let e=0;e<a.trList.length;e++){let n=a.trList[e];for(let e=0;e<n.tdList.length;e++){let i=n.tdList[e];r+=t(i.value)}}}else if(a.type===`hyperlink`){let e=a.hyperlinkId,o=[];for(;i<n.length;){let t=n[i];if(e!==t.hyperlinkId){i--;break}delete t.type,o.push(t),i++}r+=t(o)}else if(a.type===`latex`)r+=a.value;else if(a.controlId){if(!a.control?.hide){let e=a.controlId,o=[];for(;i<n.length;){let t=n[i];if(e!==t.controlId){i--;break}t.controlComponent===`value`&&(delete t.controlId,o.push(t)),i++}r+=t(o)}}else(!a.type||a.type===`text`)&&!a.area?.hide&&(r+=a.value);i++}return r}function n(e){let t=[],n=``,r=()=>{n&&=(t.push(n),``)},i=e=>e<=32||e===160||e>=8192&&e<=8202||e===8239||e===12288||e>=8203&&e<=8207||e>=8234&&e<=8238||e===8288||e===65279,a=e=>e>=48&&e<=57||e>=65&&e<=90||e>=97&&e<=122,o=e=>e>=33&&e<=47||e>=58&&e<=64||e>=91&&e<=96||e>=123&&e<=126,s=e=>e===123||e===125;for(let c of e){let e=c.charCodeAt(0);if(i(e)){r();continue}if(a(e)||s(e)||o(e)){n+=c;continue}r(),t.push(c)}return r(),t}onmessage=e=>{let r=e.data,i=n(t(r).replace(RegExp(`^​`),``).replace(RegExp(`​`,`g`),`\n`));postMessage(i.length)}})();\n//# sourceMappingURL=wordCount-BWZRHbSB.js.map", ya = typeof self < "u" && self.Blob && new Blob(["(self.URL || self.webkitURL).revokeObjectURL(self.location.href);", va], { type: "text/javascript;charset=utf-8" });
function ba(e) {
	let t;
	try {
		if (t = ya && (self.URL || self.webkitURL).createObjectURL(ya), !t) throw "";
		let n = new Worker(t, { name: e?.name });
		return n.addEventListener("error", () => {
			(self.URL || self.webkitURL).revokeObjectURL(t);
		}), n;
	} catch {
		return new Worker("data:text/javascript;charset=utf-8," + encodeURIComponent(va), { name: e?.name });
	}
}
//#endregion
//#region src/editor/core/worker/works/catalog.ts?worker&inline
var xa = "(function(){let e={first:1,second:2,third:3,fourth:4,fifth:5,sixth:6},t=[`text`,`hyperlink`,`subscript`,`superscript`,`control`,`date`,`label`];function n(e){return!e.type||t.includes(e.type)}function r(t){let{elementList:r,positionList:i}=t,a=[],o=0;for(;o<r.length;){let e=r[o],t=(e,t,r)=>{let a=e.titleId,s={type:`title`,value:``,level:e.level,titleId:a,pageNo:i[o].pageNo},c=[];for(;r<t.length;){let e=t[r];if(a!==e.titleId){r--;break}c.push(e),r++}return s.value=c.filter(e=>n(e)).map(e=>e.value).join(``).replace(RegExp(`​`,`g`),``),{position:r,titleElement:s}};if(e.titleId){let{position:n,titleElement:i}=t(e,r,o);o=n,a.push(i)}if(e.type===`table`){let n=e.trList;for(let e=0;e<n.length;e++){let r=n[e];for(let e=0;e<r.tdList.length;e++){let n=r.tdList[e].value;if(n.length>1){let e=1;for(;e<n.length;){if(n[e]?.titleId){let{titleElement:r,position:i}=t(n[e],n,e);a.push(r),e=i}e++}}}}}o++}if(!a.length)return null;let s=(t,n)=>{let r=n.subCatalog[n.subCatalog.length-1],i=e[r?.level],a=e[t.level];r&&a>i?s(t,r):n.subCatalog.push({id:t.titleId,name:t.value,level:t.level,pageNo:t.pageNo,subCatalog:[]})},c=[];for(let t=0;t<a.length;t++){let n=a[t],r=c[c.length-1],i=e[r?.level],o=e[n.level];r&&o>i?s(n,r):c.push({id:n.titleId,name:n.value,level:n.level,pageNo:n.pageNo,subCatalog:[]})}return c}onmessage=e=>{let t=e.data,n=r(t);postMessage(n)}})();\n//# sourceMappingURL=catalog-B-cbxN0s.js.map", Sa = typeof self < "u" && self.Blob && new Blob(["(self.URL || self.webkitURL).revokeObjectURL(self.location.href);", xa], { type: "text/javascript;charset=utf-8" });
function Ca(e) {
	let t;
	try {
		if (t = Sa && (self.URL || self.webkitURL).createObjectURL(Sa), !t) throw "";
		let n = new Worker(t, { name: e?.name });
		return n.addEventListener("error", () => {
			(self.URL || self.webkitURL).revokeObjectURL(t);
		}), n;
	} catch {
		return new Worker("data:text/javascript;charset=utf-8," + encodeURIComponent(xa), { name: e?.name });
	}
}
//#endregion
//#region src/editor/core/worker/works/group.ts?worker&inline
var wa = "(function(){function e(t){let n=[];for(let r of t){if(r.type===`table`){let t=r.trList;for(let r=0;r<t.length;r++){let i=t[r];for(let t=0;t<i.tdList.length;t++){let r=i.tdList[t];n.push(...e(r.value))}}}if(r.groupIds)for(let e of r.groupIds)n.includes(e)||n.push(e)}return n}onmessage=t=>{let n=t.data,r=e(n);postMessage(r)}})();\n//# sourceMappingURL=group-BZtj1M7o.js.map", Ta = typeof self < "u" && self.Blob && new Blob(["(self.URL || self.webkitURL).revokeObjectURL(self.location.href);", wa], { type: "text/javascript;charset=utf-8" });
function Ea(e) {
	let t;
	try {
		if (t = Ta && (self.URL || self.webkitURL).createObjectURL(Ta), !t) throw "";
		let n = new Worker(t, { name: e?.name });
		return n.addEventListener("error", () => {
			(self.URL || self.webkitURL).revokeObjectURL(t);
		}), n;
	} catch {
		return new Worker("data:text/javascript;charset=utf-8," + encodeURIComponent(wa), { name: e?.name });
	}
}
//#endregion
//#region src/editor/core/worker/works/value.ts?worker&inline
var Da = "(function(){let e=function(e){return e.HALF=`half`,e.ONE_THIRD=`one-third`,e.QUARTER=`quarter`,e}({}),t=function(e){return e.ARABIC=`arabic`,e.CHINESE=`chinese`,e}({});e.HALF,e.ONE_THIRD,e.QUARTER;function n(e){if(typeof structuredClone==`function`)return structuredClone(e);if(!e||typeof e!=`object`)return e;let t={};return Array.isArray(e)?t=e.map(e=>n(e)):Object.keys(e).forEach(r=>{t[r]=n(e[r])}),t}function r(e,t){let n={};for(let r in e)t.includes(r)&&(n[r]=e[r]);return n}function i(e,t){return e.length===t.length&&!e.some(e=>!t.includes(e))}let a=function(e){return e.TEXT=`text`,e.IMAGE=`image`,e.TABLE=`table`,e.HYPERLINK=`hyperlink`,e.SUPERSCRIPT=`superscript`,e.SUBSCRIPT=`subscript`,e.SEPARATOR=`separator`,e.PAGE_BREAK=`pageBreak`,e.CONTROL=`control`,e.AREA=`area`,e.CHECKBOX=`checkbox`,e.RADIO=`radio`,e.LATEX=`latex`,e.TAB=`tab`,e.DATE=`date`,e.BLOCK=`block`,e.TITLE=`title`,e.LIST=`list`,e.LABEL=`label`,e}({}),o=[`rowFlex`,`rowMargin`],s=`type.font.size.bold.color.italic.highlight.underline.strikeout.rowFlex.rowMargin.dashArray.trList.tableToolDisabled.borderType.borderColor.translateX.width.height.url.colgroup.valueList.control.checkbox.radio.dateFormat.block.level.title.listType.listStyle.listWrap.listLevel.groupIds.conceptId.imgDisplay.imgFloatPosition.imgToolDisabled.imgPreviewDisabled.imgCrop.imgCaption.textDecoration.extension.externalId.areaId.area.hide.label.labelId.lineWidth.trace.paperDirection.hint`.split(`.`),c=[`conceptId`,`extension`,`externalId`,`verticalAlign`,`backgroundColor`,`borderTypes`,`slashTypes`,`disabled`,`deletable`],l=[`tdId`,`trId`,`tableId`],u=[`level`,`titleId`,`title`],d=[`listId`,`listType`,`listStyle`,`listLevel`],f=[`font`,`size`,`bold`,`highlight`,`italic`,`strikeout`],p=[`areaId`,`area`];[...l,...u,...d,...p],a.TEXT,a.HYPERLINK,a.SUBSCRIPT,a.SUPERSCRIPT,a.CONTROL,a.DATE,a.IMAGE,a.LATEX,a.BLOCK,a.PAGE_BREAK,a.SEPARATOR,a.TABLE,a.TITLE,a.LIST;let m=function(e){return e.UL=`ul`,e.OL=`ol`,e}({}),h=function(e){return e.DISC=`disc`,e.CIRCLE=`circle`,e.SQUARE=`square`,e.CHECKBOX=`checkbox`,e}({}),g=function(e){return e.DISC=`disc`,e.CIRCLE=`circle`,e.SQUARE=`square`,e.DECIMAL=`decimal`,e.CHECKBOX=`checkbox`,e}({});h.DISC,h.CIRCLE,h.SQUARE,h.CHECKBOX,m.OL,m.UL,g.DISC,g.CIRCLE,g.SQUARE,g.DECIMAL,g.CHECKBOX;let _=function(e){return e.FIRST=`first`,e.SECOND=`second`,e.THIRD=`third`,e.FOURTH=`fourth`,e.FIFTH=`fifth`,e.SIXTH=`sixth`,e}({});_.FIRST,_.SECOND,_.THIRD,_.FOURTH,_.FIFTH,_.SIXTH,_.FIRST,_.SECOND,_.THIRD,_.FOURTH,_.FIFTH,_.SIXTH,_.FIRST,_.SECOND,_.THIRD,_.FOURTH,_.FIFTH,_.SIXTH;let v=function(e){return e.PREFIX=`prefix`,e.POSTFIX=`postfix`,e.PRE_TEXT=`preText`,e.POST_TEXT=`postText`,e.PLACEHOLDER=`placeholder`,e.VALUE=`value`,e.CHECKBOX=`checkbox`,e.RADIO=`radio`,e}({}),y=function(e){return e.LEFT=`left`,e.CENTER=`center`,e.RIGHT=`right`,e.ALIGNMENT=`alignment`,e.JUSTIFY=`justify`,e}({}),b=function(e){return e.CONTAIN=`contain`,e.COVER=`cover`,e}({}),x=function(e){return e.REPEAT=`repeat`,e.NO_REPEAT=`no-repeat`,e.REPEAT_X=`repeat-x`,e.REPEAT_Y=`repeat-y`,e}({});b.COVER,x.NO_REPEAT;let S=function(e){return e.TOP=`top`,e.MIDDLE=`middle`,e.BOTTOM=`bottom`,e}({});S.BOTTOM,e.HALF,e.HALF,y.CENTER,{PAGE_NO:`{pageNo}`,PAGE_COUNT:`{pageCount}`}.PAGE_NO,t.ARABIC,S.BOTTOM;let C=function(e){return e.TEXT=`text`,e.IMAGE=`image`,e}({}),w=function(e){return e.BOTTOM=`bottom`,e.TOP=`top`,e}({});C.TEXT,t.ARABIC,w.BOTTOM,function(e){return e.PAGE=`page`,e.CONTINUITY=`continuity`,e}({}).CONTINUITY;function T(e,t){let n=Object.keys(e),r=Object.keys(t);if(n.length!==r.length)return!1;for(let r=0;r<n.length;r++){let a=n[r];if(a!==`value`&&!(a===`groupIds`&&Array.isArray(e[a])&&Array.isArray(t[a])&&i(e[a],t[a]))){if(a===`trace`){let n=e[a]||[],r=t[a]||[];if(n.length!==r.length)return!1;for(let e=0;e<n.length;e++){let t=n[e],i=r[e];if(t.type!==i.type||t.author!==i.author||t.timestamp!==i.timestamp)return!1}continue}if(e[a]!==t[a])return!1}}return!0}function E(e,t={}){let{extraPickAttrs:n}=t,r=[...s];n&&r.push(...n);let i={value:e.value===`​`?`\n`:e.value};return r.forEach(t=>{let n=e[t];n!==void 0&&(i[t]=n)}),i}function D(e,t={}){let{extraPickAttrs:i,isClassifyArea:s=!1,isClone:l=!0,isListValue:u=!1}=t,d=l?n(e):e,p=[],m=0;for(;m<d.length;){let e=d[m];if(m===0&&e.value===`​`&&!e.listId&&(!e.type||e.type===a.TEXT)){m++;continue}if(e.areaId){let n=e.areaId,r=e.area,i=[];for(;m<d.length;){let e=d[m];if(n!==e.areaId){m--;break}delete e.area,delete e.areaId,i.push(e),m++}let o=D(i,t);if(s){let t={type:a.AREA,value:``,areaId:n,area:r};t.valueList=o,e=t}else{p.splice(m,0,...o);continue}}else if(e.titleId&&e.level){let n=e.titleId;if(n){let r=e.level,i={type:a.TITLE,title:e.title,titleId:n,value:``,level:r},o=[];for(;m<d.length;){let e=d[m];if(n!==e.titleId){m--;break}delete e.level,delete e.title,o.push(e),m++}i.valueList=D(o,t),e=i}}else if(!u&&e.listId&&e.listType){let n=e.listId;if(n){let r=e.listType,i=e.listStyle,o={type:a.LIST,value:``,listId:n,listType:r,listStyle:i},s=[];for(;m<d.length;){let e=d[m];if(!e.listId||r!==e.listType){m--;break}delete e.listType,delete e.listStyle,s.push(e),m++}o.valueList=D(s,{...t,isListValue:!0}),e=o}}else if(e.type===a.TABLE){if(e.trList)for(let n=0;n<e.trList.length;n++){let r=e.trList[n];delete r.id;for(let e=0;e<r.tdList.length;e++){let n=r.tdList[e],i={colspan:n.colspan,rowspan:n.rowspan,value:D(n.value,{...t,isClassifyArea:!0})};c.forEach(e=>{let t=n[e];t!==void 0&&(i[e]=t)}),r.tdList[e]=i}}}else if(e.type===a.HYPERLINK){let n=e.hyperlinkId;if(n){let r={type:a.HYPERLINK,value:``,url:e.url},i=[];for(;m<d.length;){let e=d[m];if(n!==e.hyperlinkId){m--;break}delete e.type,delete e.url,i.push(e),m++}r.valueList=D(i,t),e=r}}else if(e.type===a.DATE){let n=e.dateId;if(n){let r={type:a.DATE,value:``,dateFormat:e.dateFormat},i=[];for(;m<d.length;){let e=d[m];if(n!==e.dateId){m--;break}delete e.type,delete e.dateFormat,i.push(e),m++}r.valueList=D(i,t),e=r}}else if(e.controlId){let n=e.controlId;if(e.controlComponent===v.PREFIX){let s=[],c=!1,l=m;for(;l<d.length;){let e=d[l];if(e.controlId===n){if(e.controlComponent===v.VALUE&&(delete e.control,delete e.controlId,s.push(e)),e.controlComponent===v.POSTFIX){c=!0,l++;break}l++;continue}if(e.controlComponent===v.PREFIX){let n=l;for(;n<d.length;){let t=d[n];if(t.controlId===e.controlId&&t.controlComponent===v.POSTFIX)break;n++}let r=D(d.slice(l,Math.min(n+1,d.length)),t)[0];r&&s.push(r),l=n+1;continue}break}if(c){let c=r(e,f),u={...e.control,...c},d={...r(e,o),type:a.CONTROL,value:``,control:u,controlId:n,trace:e.trace};d.control.value=D(s,t),e=E(d,{extraPickAttrs:i}),m+=l-m-1}}if(e.controlComponent&&(delete e.control,delete e.controlId,e.controlComponent!==v.VALUE&&e.controlComponent!==v.PRE_TEXT&&e.controlComponent!==v.POST_TEXT)){m++;continue}}let n=E(e,{extraPickAttrs:i});if(!e.type||e.type===a.TEXT||e.type===a.SUBSCRIPT||e.type===a.SUPERSCRIPT)for(;m<d.length;){let e=d[m+1];if(m++,e&&T(n,E(e,{extraPickAttrs:i}))){let t=e.value===`​`?`\n`:e.value;n.value+=t}else break}else m++;p.push(n)}return p}onmessage=e=>{let{options:t,data:n}=e.data,{extraPickAttrs:r=[]}=t||{},i={header:D(n.header,{extraPickAttrs:r,isClone:!1}),main:D(n.main,{extraPickAttrs:r,isClassifyArea:!0,isClone:!1}),footer:D(n.footer,{extraPickAttrs:r,isClone:!1})};postMessage(i)}})();\n//# sourceMappingURL=value-CLcLo2uw.js.map", Oa = typeof self < "u" && self.Blob && new Blob(["(self.URL || self.webkitURL).revokeObjectURL(self.location.href);", Da], { type: "text/javascript;charset=utf-8" });
function ka(e) {
	let t;
	try {
		if (t = Oa && (self.URL || self.webkitURL).createObjectURL(Oa), !t) throw "";
		let n = new Worker(t, { name: e?.name });
		return n.addEventListener("error", () => {
			(self.URL || self.webkitURL).revokeObjectURL(t);
		}), n;
	} catch {
		return new Worker("data:text/javascript;charset=utf-8," + encodeURIComponent(Da), { name: e?.name });
	}
}
//#endregion
//#region src/editor/core/worker/WorkerManager.ts
var Aa = class {
	draw;
	wordCountWorker;
	catalogWorker;
	groupWorker;
	valueWorker;
	constructor(e) {
		this.draw = e, this.wordCountWorker = new ba(), this.catalogWorker = new Ca(), this.groupWorker = new Ea(), this.valueWorker = new ka();
	}
	getWordCount() {
		return new Promise((e, t) => {
			this.wordCountWorker.onmessage = (t) => {
				e(t.data);
			}, this.wordCountWorker.onerror = (e) => {
				t(e);
			};
			let n = this.draw.getOriginalMainElementList();
			this.wordCountWorker.postMessage(n);
		});
	}
	getCatalog() {
		return new Promise((e, t) => {
			this.catalogWorker.onmessage = (t) => {
				e(t.data);
			}, this.catalogWorker.onerror = (e) => {
				t(e);
			};
			let n = this.draw.getOriginalMainElementList(), r = this.draw.getPosition().getOriginalMainPositionList();
			this.catalogWorker.postMessage({
				elementList: n,
				positionList: r
			});
		});
	}
	getGroupIds() {
		return new Promise((e, t) => {
			this.groupWorker.onmessage = (t) => {
				e(t.data);
			}, this.groupWorker.onerror = (e) => {
				t(e);
			};
			let n = this.draw.getOriginalMainElementList();
			this.groupWorker.postMessage(n);
		});
	}
	getValue(t) {
		return new Promise((n, r) => {
			this.valueWorker.onmessage = (t) => {
				n({
					version: e,
					data: t.data,
					options: k(this.draw.getOptions())
				});
			}, this.valueWorker.onerror = (e) => {
				r(e);
			}, this.valueWorker.postMessage({
				data: this.draw.getOriginValue(t),
				options: t
			});
		});
	}
	destroy() {
		this.wordCountWorker.terminate(), this.catalogWorker.terminate(), this.groupWorker.terminate(), this.valueWorker.terminate();
	}
}, ja = class {
	container;
	canvas;
	draw;
	options;
	curElement;
	curElementSrc;
	previewerDrawOption;
	curPosition;
	eventBus;
	imageList;
	curShowElement;
	imageCount;
	imagePre;
	imageNext;
	resizerSelection;
	resizerHandleList;
	resizerImageContainer;
	resizerImage;
	resizerSize;
	width;
	height;
	mousedownX;
	mousedownY;
	curHandleIndex;
	previewerContainer;
	previewerImage;
	constructor(e) {
		this.container = e.getContainer(), this.canvas = e.getPage(), this.draw = e, this.options = e.getOptions(), this.curElement = null, this.curElementSrc = "", this.previewerDrawOption = {}, this.curPosition = null, this.eventBus = e.getEventBus(), this.imageList = [], this.curShowElement = null, this.imageCount = null, this.imagePre = null, this.imageNext = null;
		let { resizerSelection: t, resizerHandleList: n, resizerImageContainer: r, resizerImage: i, resizerSize: a } = this._createResizerDom();
		this.resizerSelection = t, this.resizerHandleList = n, this.resizerImageContainer = r, this.resizerImage = i, this.resizerSize = a, this.width = 0, this.height = 0, this.mousedownX = 0, this.mousedownY = 0, this.curHandleIndex = 0, this.previewerContainer = null, this.previewerImage = null;
	}
	_getElementPosition(e, t = null) {
		let n = 0, r = 0, i = t?.pageNo ?? this.draw.getPageNo(), { x: a, y: o } = this.draw.getPageOffset(i);
		if (e.imgFloatPosition) {
			let t = this.draw.getPosition(), i = t.getFloatPositionByElement(e);
			if (i) {
				let e = t.getFloatPositionCoordinate(i);
				n = e.x + a, r = e.y + o;
			}
		} else if (t) {
			let { coordinate: { leftTop: [e, i] }, ascent: s } = t;
			n = e + a, r = i + o + s;
		}
		return {
			x: n,
			y: r
		};
	}
	_createResizerDom() {
		let { scale: e } = this.options, t = document.createElement("div");
		t.classList.add("ce-resizer-selection"), t.style.display = "none", t.style.borderColor = this.options.resizerColor, t.style.borderWidth = `${e}px`;
		let n = [];
		for (let e = 0; e < 8; e++) {
			let r = document.createElement("div");
			r.style.background = this.options.resizerColor, r.classList.add("resizer-handle"), r.classList.add(`handle-${e}`), r.setAttribute("data-index", String(e)), r.onmousedown = this._mousedown.bind(this), t.append(r), n.push(r);
		}
		this.container.append(t);
		let r = document.createElement("div");
		r.classList.add("ce-resizer-size-view");
		let i = document.createElement("span");
		r.append(i), t.append(r);
		let a = document.createElement("div");
		a.classList.add("ce-resizer-image"), a.style.display = "none";
		let o = document.createElement("img");
		return a.append(o), this.container.append(a), {
			resizerSelection: t,
			resizerHandleList: n,
			resizerImageContainer: a,
			resizerImage: o,
			resizerSize: i
		};
	}
	_keydown = () => {
		this.resizerSelection.style.display === "block" && (this.clearResizer(), document.removeEventListener("keydown", this._keydown));
	};
	_mousedown(e) {
		if (this.canvas = this.draw.getPage(), !this.curElement) return;
		let { scale: t } = this.options;
		this.mousedownX = e.x, this.mousedownY = e.y;
		let n = e.target;
		this.curHandleIndex = Number(n.dataset.index);
		let r = window.getComputedStyle(n).cursor;
		document.body.style.cursor = r, this.canvas.style.cursor = r, this.resizerImage.src = this.curElementSrc, this.resizerImageContainer.style.display = "block";
		let { x: i, y: a } = this._getElementPosition(this.curElement, this.curPosition);
		this.resizerImageContainer.style.left = `${i}px`, this.resizerImageContainer.style.top = `${a}px`, this.resizerImage.style.width = `${this.curElement.width * t}px`, this.resizerImage.style.height = `${this.curElement.height * t}px`;
		let o = this._mousemove.bind(this);
		document.addEventListener("mousemove", o), document.addEventListener("mouseup", () => {
			this.curElement && !this.previewerDrawOption.dragDisable && (this.curElement.width = this.width, this.curElement.height = this.height, this.draw.render({
				isSetCursor: !0,
				curIndex: this.curPosition?.index
			})), this.resizerImageContainer.style.display = "none", document.removeEventListener("mousemove", o), document.body.style.cursor = "", this.canvas.style.cursor = "text";
		}, { once: !0 }), e.preventDefault();
	}
	_mousemove(e) {
		if (!this.curElement || this.previewerDrawOption.dragDisable) return;
		let { scale: t } = this.options, n = 0, r = 0;
		switch (this.curHandleIndex) {
			case 0:
				{
					let t = this.mousedownX - e.x, i = this.mousedownY - e.y;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.curElement.height * n / this.curElement.width;
				}
				break;
			case 1:
				r = this.mousedownY - e.y;
				break;
			case 2:
				{
					let t = e.x - this.mousedownX, i = this.mousedownY - e.y;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.curElement.height * n / this.curElement.width;
				}
				break;
			case 4:
				{
					let t = e.x - this.mousedownX, i = e.y - this.mousedownY;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.curElement.height * n / this.curElement.width;
				}
				break;
			case 3:
				n = e.x - this.mousedownX;
				break;
			case 5:
				r = e.y - this.mousedownY;
				break;
			case 6:
				{
					let t = this.mousedownX - e.x, i = e.y - this.mousedownY;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.curElement.height * n / this.curElement.width;
				}
				break;
			case 7: n = this.mousedownX - e.x;
		}
		let i = this.curElement.width + n / t, a = this.curElement.height + r / t;
		if (i <= 0 || a <= 0) return;
		this.width = i, this.height = a;
		let o = i * t, s = a * t;
		this.resizerImage.style.width = `${o}px`, this.resizerImage.style.height = `${s}px`, this._updateResizerRect(o, s), this._updateResizerSizeView(o, s), e.preventDefault(), this.eventBus.isSubscribe("imageSizeChange") && this.eventBus.emit("imageSizeChange", { element: this.curElement });
	}
	_drawPreviewer() {
		let e = document.createElement("div");
		e.classList.add("ce-image-previewer");
		let t = document.createElement("i");
		t.classList.add("image-close"), t.onclick = () => {
			this._clearPreviewer();
		}, e.append(t);
		let n = document.createElement("div");
		n.classList.add("ce-image-container");
		let r = document.createElement("img");
		r.src = this.curElementSrc, r.draggable = !1, n.append(r), this.previewerImage = r, e.append(n);
		let i = 0, a = 0, o = 1, s = 0, c = document.createElement("div");
		c.classList.add("ce-image-menu");
		let l = document.createElement("div");
		l.classList.add("image-navigate");
		let u = document.createElement("i");
		u.classList.add("image-pre"), u.onclick = () => {
			let e = this.imageList.findIndex((e) => e.id === this.curShowElement?.id);
			e <= 0 || (this.curShowElement = this.imageList[e - 1], r.src = this.curShowElement.value, this._updateImageNavigate());
		}, l.append(u), this.imagePre = u;
		let d = document.createElement("span");
		d.classList.add("image-count"), this.imageCount = d, l.append(d);
		let f = document.createElement("i");
		f.classList.add("image-next"), f.onclick = () => {
			let e = this.imageList.findIndex((e) => e.id === this.curShowElement?.id);
			e >= this.imageList.length - 1 || (this.curShowElement = this.imageList[e + 1], r.src = this.curShowElement.value, this._updateImageNavigate());
		}, this.imageNext = f, l.append(f), c.append(l);
		let p = document.createElement("i");
		p.classList.add("zoom-in"), p.onclick = () => {
			o += .1, this._setPreviewerTransform(o, s, i, a);
		}, c.append(p);
		let m = document.createElement("i");
		m.onclick = () => {
			o - .1 <= .1 || (o -= .1, this._setPreviewerTransform(o, s, i, a));
		}, m.classList.add("zoom-out"), c.append(m);
		let h = document.createElement("i");
		h.classList.add("rotate"), h.onclick = () => {
			s += 1, this._setPreviewerTransform(o, s, i, a);
		}, c.append(h);
		let g = document.createElement("i");
		g.classList.add("original-size"), g.onclick = () => {
			i = 0, a = 0, o = 1, s = 0, this._setPreviewerTransform(o, s, i, a);
		}, c.append(g);
		let _ = document.createElement("i");
		_.classList.add("image-download"), _.onclick = () => {
			let { mime: e } = this.previewerDrawOption;
			ee(r.src, `${this.curElement?.id}.${e || "png"}`);
		}, c.append(_), e.append(c), this.previewerContainer = e, document.body.append(e);
		let v = 0, y = 0, b = !1;
		r.onmousedown = (t) => {
			b = !0, v = t.x, y = t.y, e.style.cursor = "move";
		}, e.onmousemove = (e) => {
			b && (i += e.x - v, a += e.y - y, v = e.x, y = e.y, this._setPreviewerTransform(o, s, i, a));
		}, e.onmouseup = () => {
			b = !1, e.style.cursor = "auto";
		}, e.onwheel = (e) => {
			if (e.preventDefault(), e.stopPropagation(), e.deltaY < 0) o += .1;
			else {
				if (o - .1 <= .1) return;
				o -= .1;
			}
			this._setPreviewerTransform(o, s, i, a);
		}, this._updateImageNavigate();
	}
	_updateImageNavigate() {
		let e = this.imageList.findIndex((e) => e.id === this.curShowElement?.id);
		this.imageCount.innerText = `${e + 1} / ${this.imageList.length}`, e <= 0 ? this.imagePre.classList.add("disabled") : this.imagePre.classList.remove("disabled"), e >= this.imageList.length - 1 ? this.imageNext.classList.add("disabled") : this.imageNext.classList.remove("disabled");
	}
	_setPreviewerTransform(e, t, n, r) {
		this.previewerImage && (this.previewerImage.style.left = `${n}px`, this.previewerImage.style.top = `${r}px`, this.previewerImage.style.transform = `scale(${e}) rotate(${t * 90}deg)`);
	}
	_clearPreviewer() {
		this.previewerContainer?.remove(), this.previewerContainer = null, document.body.style.overflow = "auto";
	}
	_updateResizerRect(e, t) {
		let { resizerSize: n, scale: r } = this.options, i = this.draw.isReadonly();
		this.resizerSelection.style.width = `${e}px`, this.resizerSelection.style.height = `${t}px`;
		for (let a = 0; a < 8; a++) {
			let o = a === 0 || a === 6 || a === 7 ? -n : a === 1 || a === 5 ? e / 2 : e - n, s = a === 0 || a === 1 || a === 2 ? -n : a === 3 || a === 7 ? t / 2 - n : t - n;
			this.resizerHandleList[a].style.transform = `scale(${r})`, this.resizerHandleList[a].style.left = `${o}px`, this.resizerHandleList[a].style.top = `${s}px`, this.resizerHandleList[a].style.display = i ? "none" : "block";
		}
	}
	_updateResizerSizeView(e, t) {
		this.resizerSize.innerText = `${Math.round(e)} × ${Math.round(t)}`;
	}
	render() {
		let e = this.draw.getMode();
		!this.curElement || this.curElement.imgToolDisabled && !this.draw.isDesignMode() || e === p.PRINT && this.options.modeRule[p.PRINT]?.imagePreviewerDisabled || e === p.READONLY && this.options.modeRule[p.READONLY]?.imagePreviewerDisabled || (this.imageList = this.draw.getImageParticle().getOriginalMainImageList(), this.curShowElement = this.curElement, this._drawPreviewer(), document.body.style.overflow = "hidden");
	}
	drawResizer(e, t = null, n = {}) {
		let r = this.draw.getMode();
		e.imgToolDisabled && !this.draw.isDesignMode() || r === p.PRINT && this.options.modeRule[p.PRINT]?.imagePreviewerDisabled || r === p.READONLY && this.options.modeRule[p.READONLY]?.imagePreviewerDisabled || (this.previewerDrawOption = n, this.curElementSrc = e[n.srcKey || "value"] || "", this.updateResizer(e, t), document.addEventListener("keydown", this._keydown));
	}
	updateResizer(e, t = null) {
		let { scale: n } = this.options, r = e.width * n, i = e.height * n;
		this._updateResizerSizeView(r, i);
		let { x: a, y: o } = this._getElementPosition(e, t);
		this.resizerSelection.style.left = `${a}px`, this.resizerSelection.style.top = `${o}px`, this.resizerSelection.style.borderWidth = `${n}px`, this._updateResizerRect(r, i), this.resizerSelection.style.display = "block", this.curElement = e, this.curPosition = t, this.width = r, this.height = i;
	}
	clearResizer() {
		this.resizerSelection.style.display = "none", document.removeEventListener("keydown", this._keydown);
	}
}, Ma = class {
	draw;
	range;
	datePicker;
	options;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.range = e.getRange(), this.datePicker = new Fi(e, { onSubmit: this._setValue.bind(this) });
	}
	_setValue(e) {
		if (!e) return;
		let t = this.getDateElementRange();
		if (!t) return;
		let [n, r] = t, i = this.draw.getElementList(), a = i[n + 1];
		this.draw.deleteElementList(i, n + 1, r - n), this.range.setRange(n, n);
		let o = {
			type: H.DATE,
			value: "",
			dateFormat: a.dateFormat,
			valueList: [{ value: e }]
		};
		kn(i, [o], n, { editorOptions: this.options }), this.draw.insertElementList([o]);
	}
	getDateElementRange() {
		let e = -1, t = -1, { startIndex: n, endIndex: r } = this.range.getRange();
		if (!~n && !~r) return null;
		let i = this.draw.getElementList(), a = i[n];
		if (a.type !== H.DATE) return null;
		let o = n;
		for (; o >= 0;) {
			if (i[o].dateId !== a.dateId) {
				e = o;
				break;
			}
			o--;
		}
		let s = n + 1;
		for (; s < i.length;) {
			if (i[s].dateId !== a.dateId) {
				t = s - 1;
				break;
			}
			s++;
		}
		return s === i.length && (t = s - 1), !~e || !~t ? null : [e, t];
	}
	clearDatePicker() {
		this.datePicker.dispose();
	}
	renderDatePicker(e, t) {
		let n = this.draw.getElementList(), r = this.getDateElementRange(), i = r ? n.slice(r[0] + 1, r[1] + 1).map((e) => e.value).join("") : "";
		this.datePicker.render({
			value: i,
			position: t,
			dateFormat: e.dateFormat
		});
	}
}, Na = class {
	element;
	videoCache;
	constructor(e) {
		this.element = e, this.videoCache = /* @__PURE__ */ new Map();
	}
	snapshot(e, t, n) {
		return new Promise((r, i) => {
			let a = this.element.block?.videoBlock?.src || "";
			if (this.videoCache.has(a)) {
				let i = this.videoCache.get(a);
				e.drawImage(i, t, n, this.element.metrics.width, this.element.metrics.height), r(this.element);
			} else {
				let o = document.createElement("video");
				o.src = a, o.muted = !0, o.crossOrigin = "anonymous", o.onloadeddata = () => {
					e.drawImage(o, t, n, this.element.metrics.width, this.element.metrics.height), this.videoCache.set(a, o), r(this.element);
				}, o.onerror = (e) => {
					i(e);
				}, o.play().then(() => {
					o.pause();
				});
			}
		});
	}
	render(e) {
		let t = this.element.block, n = document.createElement("video");
		n.style.width = "100%", n.style.height = "100%", n.style.objectFit = "contain", n.src = t.videoBlock?.src || "", n.controls = !0, e.append(n);
	}
}, Pa = class {
	draw;
	options;
	element;
	block;
	blockContainer;
	blockItem;
	positionInfo = null;
	blockCache;
	resizerMask;
	resizerSelection;
	resizerHandleList;
	width;
	height;
	mousedownX;
	mousedownY;
	curHandleIndex;
	isAllowResize;
	constructor(e, t) {
		this.draw = e.getDraw(), this.options = this.draw.getOptions(), this.blockContainer = e.getBlockContainer(), this.element = t, this.block = null;
		let { blockItem: n, resizerMask: r, resizerSelection: i, resizerHandleList: a } = this._createBlockItem();
		this.blockItem = n, this.blockContainer.append(this.blockItem), this.blockCache = /* @__PURE__ */ new Map(), this.resizerMask = r, this.resizerSelection = i, this.resizerHandleList = a, this.width = 0, this.height = 0, this.mousedownX = 0, this.mousedownY = 0, this.curHandleIndex = 0, this.isAllowResize = !1;
	}
	getBlockElement() {
		return this.element;
	}
	getBlockWidth() {
		return this.element.width || this.element.metrics.width;
	}
	getIFrameBlock() {
		return this.block instanceof Ge ? this.block : null;
	}
	getPositionInfo() {
		return this.positionInfo;
	}
	_createBlockItem() {
		let { scale: e, resizerColor: t } = this.options, n = document.createElement("div");
		n.classList.add("ce-block-item");
		let r = document.createElement("div");
		r.style.display = "none", r.classList.add("ce-resizer-selection"), r.style.borderColor = t, r.style.borderWidth = `${e}px`;
		let i = [];
		for (let e = 0; e < 8; e++) {
			let n = document.createElement("div");
			n.style.background = t, n.classList.add("resizer-handle"), n.classList.add(`handle-${e}`), n.setAttribute("data-index", String(e)), n.onmousedown = this._mousedown.bind(this), r.append(n), i.push(n);
		}
		let a = document.createElement("div");
		return a.classList.add("ce-resizer-mask"), a.style.display = "none", n.append(a), n.onmouseenter = () => {
			if (this.draw.isReadonly()) return;
			let { width: e, height: t } = this.element.metrics;
			this._updateResizerRect(e, t), r.style.display = "block";
		}, n.onmouseleave = () => {
			this.isAllowResize || (r.style.display = "none");
		}, n.append(r), {
			blockItem: n,
			resizerMask: a,
			resizerSelection: r,
			resizerHandleList: i
		};
	}
	_updateResizerRect(e, t) {
		let { resizerSize: n, scale: r } = this.options;
		this.resizerSelection.style.width = `${e}px`, this.resizerSelection.style.height = `${t}px`;
		for (let i = 0; i < 8; i++) {
			let a = i === 0 || i === 6 || i === 7 ? -n : i === 1 || i === 5 ? e / 2 : e - n, o = i === 0 || i === 1 || i === 2 ? -n : i === 3 || i === 7 ? t / 2 - n : t - n;
			this.resizerHandleList[i].style.transform = `scale(${r})`, this.resizerHandleList[i].style.left = `${a}px`, this.resizerHandleList[i].style.top = `${o}px`;
		}
	}
	_mousedown(e) {
		let t = this.draw.getPage();
		this.mousedownX = e.x, this.mousedownY = e.y, this.isAllowResize = !0;
		let n = e.target;
		this.curHandleIndex = Number(n.dataset.index), this.resizerMask.style.display = "block";
		let r = window.getComputedStyle(n).cursor;
		document.body.style.cursor = r, t.style.cursor = r;
		let i = this._mousemove.bind(this);
		document.addEventListener("mousemove", i), document.addEventListener("mouseup", () => {
			this.element.width = Math.min(this.width, this.draw.getInnerWidth()), this.element.height = this.height, this.isAllowResize = !1, this.resizerSelection.style.display = "none", this.resizerMask.style.display = "none", document.removeEventListener("mousemove", i), document.body.style.cursor = "", t.style.cursor = "text", this.draw.render();
		}, { once: !0 }), e.preventDefault();
	}
	_mousemove(e) {
		if (!this.isAllowResize) return;
		let { scale: t } = this.options, n = 0, r = 0;
		switch (this.curHandleIndex) {
			case 0:
				{
					let t = this.mousedownX - e.x, i = this.mousedownY - e.y;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.element.height * n / this.getBlockWidth();
				}
				break;
			case 1:
				r = this.mousedownY - e.y;
				break;
			case 2:
				{
					let t = e.x - this.mousedownX, i = this.mousedownY - e.y;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.element.height * n / this.getBlockWidth();
				}
				break;
			case 4:
				{
					let t = e.x - this.mousedownX, i = e.y - this.mousedownY;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.element.height * n / this.getBlockWidth();
				}
				break;
			case 3:
				n = e.x - this.mousedownX;
				break;
			case 5:
				r = e.y - this.mousedownY;
				break;
			case 6:
				{
					let t = this.mousedownX - e.x, i = e.y - this.mousedownY;
					n = Math.cbrt(t ** 3 + i ** 3), r = this.element.height * n / this.getBlockWidth();
				}
				break;
			case 7: n = this.mousedownX - e.x;
		}
		let i = this.getBlockWidth() + n / t, a = this.element.height + r / t;
		if (i <= 0 || a <= 0) return;
		this.width = i, this.height = a;
		let o = i * t, s = a * t;
		this._updateResizerRect(o, s), this.blockItem.style.width = `${o}px`, this.blockItem.style.height = `${s}px`, e.preventDefault();
	}
	snapshot(e, t, n, r) {
		let i = this.element.block;
		if (i.type === Et.VIDEO) {
			if (this.blockItem.style.display = "none", this.blockCache.has(this.element.id)) this.blockCache.get(this.element.id).snapshot(e, n, r);
			else {
				this.block = new Na(this.element);
				let t = this.block.snapshot(e, n, r);
				this.draw.getImageObserver().add(t), this.blockCache.set(this.element.id, this.block);
			}
		} else i.type === Et.IFRAME && this.setClientRects(t, n, r);
	}
	render() {
		let e = this.element.block;
		e.type === Et.IFRAME ? (this.block = new Ge(this.element), this.block.render(this.blockItem)) : e.type === Et.VIDEO && (this.block = new Na(this.element), this.block.render(this.blockItem));
	}
	setClientRects(e, t, n) {
		let { x: r, y: i } = this.draw.getPageOffset(e), { metrics: a } = this.element;
		this.blockItem.style.display = "block", this.blockItem.style.width = `${a.width}px`, this.blockItem.style.height = `${a.height}px`, this.blockItem.style.left = `${t + r}px`, this.blockItem.style.top = `${i + n}px`, this.positionInfo = {
			pageNo: e,
			x: t,
			y: n
		};
	}
	setStatus() {
		this.block instanceof Ge && this.block.setReadonly(this.draw.isReadonly());
	}
	remove() {
		this.blockItem.remove();
	}
}, Fa = class {
	draw;
	options;
	container;
	blockContainer;
	blockMap;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer(), this.blockMap = /* @__PURE__ */ new Map(), this.blockContainer = this._createBlockContainer(), this.container.append(this.blockContainer);
	}
	_createBlockContainer() {
		let e = document.createElement("div");
		return e.classList.add("ce-block-container"), e;
	}
	getDraw() {
		return this.draw;
	}
	getBlockContainer() {
		return this.blockContainer;
	}
	render(e, t, n, r, i) {
		let a = n.id, o = this.blockMap.get(a);
		o || (o = new Pa(this, n), o.render(), this.blockMap.set(a, o)), this.draw.isPrintMode() ? o.snapshot(e, t, r, i) : o.setClientRects(t, r, i), o.setStatus();
	}
	clear() {
		if (!this.blockMap.size) return;
		let e = this.draw.getOriginalMainElementList(), t = [];
		for (let n = 0; n < e.length; n++) {
			let r = e[n];
			r.type === H.BLOCK && t.push(r.id);
		}
		this.blockMap.forEach((e) => {
			let n = e.getBlockElement().id;
			t.includes(n) || (e.remove(), this.blockMap.delete(n));
		});
	}
	update() {
		this.blockMap.forEach((e) => {
			let t = e.getBlockElement();
			if (t.block?.type === Et.IFRAME && t.block.iframeBlock?.srcdoc) {
				let n = e.getIFrameBlock?.()?.getIframe?.();
				n?.contentDocument && (t.block.iframeBlock.srcdoc = n.contentDocument.documentElement.outerHTML);
			}
		});
	}
	async drawIframeToPage(e, t) {
		let n = [];
		this.blockMap.forEach((r) => {
			if (r.getBlockElement().block?.type !== Et.IFRAME) return;
			let i = r.getPositionInfo();
			if (!i) return;
			let a = r.getIFrameBlock()?.getIframe();
			if (!a) return;
			let { pageNo: o, x: s, y: c } = i, l = e[o]?.getContext("2d");
			if (!l) return;
			let { width: u, height: d } = r.getBlockElement().metrics;
			n.push(t(a).then((e) => fe(e)).then((e) => l.drawImage(e, s, c, u, d)));
		}), await Promise.allSettled(n);
	}
	pickIframeInfo() {
		let e = [], { scale: t } = this.options;
		return this.blockMap.forEach((n) => {
			let r = n.getBlockElement();
			if (!r.block?.iframeBlock || r.block.type !== Et.IFRAME) return;
			let i = n.getPositionInfo();
			if (!i) return;
			let { pageNo: a, x: o, y: s } = i;
			e[a] || (e[a] = []), e[a].push({
				x: o,
				y: s,
				width: r.metrics.width / t,
				height: r.metrics.height / t,
				src: r.block.iframeBlock.src,
				srcdoc: r.block.iframeBlock.srcdoc
			});
		}), e;
	}
}, Ia = {
	contextmenu: {
		global: {
			cut: "剪切",
			copy: "复制",
			paste: "粘贴",
			selectAll: "全选",
			print: "打印"
		},
		control: { delete: "删除控件" },
		hyperlink: {
			delete: "删除链接",
			cancel: "取消链接",
			edit: "编辑链接"
		},
		image: {
			change: "更改图片",
			saveAs: "另存为图片",
			textWrap: "文字环绕",
			textWrapType: {
				embed: "嵌入型",
				upDown: "上下型环绕",
				surround: "四周型环绕",
				floatTop: "浮于文字上方",
				floatBottom: "衬于文字下方"
			}
		},
		table: {
			insertRowCol: "插入行列",
			insertTopRow: "上方插入1行",
			insertBottomRow: "下方插入1行",
			insertLeftCol: "左侧插入1列",
			insertRightCol: "右侧插入1列",
			deleteRowCol: "删除行列",
			deleteRow: "删除1行",
			deleteCol: "删除1列",
			deleteTable: "删除整个表格",
			mergeCell: "合并单元格",
			mergeCancelCell: "取消合并",
			autoFitToContent: "根据内容自动调整表格",
			autoFitToPage: "根据窗口自动调整表格",
			verticalAlign: "垂直对齐",
			verticalAlignTop: "顶端对齐",
			verticalAlignMiddle: "垂直居中",
			verticalAlignBottom: "底端对齐",
			border: "表格边框",
			borderAll: "所有框线",
			borderEmpty: "无框线",
			borderDash: "虚框线",
			borderExternal: "外侧框线",
			borderInternal: "内侧框线",
			borderTd: "单元格边框",
			borderTdTop: "上边框",
			borderTdRight: "右边框",
			borderTdBottom: "下边框",
			borderTdLeft: "左边框",
			borderTdForward: "正斜线",
			borderTdBack: "反斜线"
		}
	},
	datePicker: {
		now: "此刻",
		confirm: "确定",
		return: "返回日期",
		timeSelect: "时间选择",
		weeks: {
			sun: "日",
			mon: "一",
			tue: "二",
			wed: "三",
			thu: "四",
			fri: "五",
			sat: "六"
		},
		year: "年",
		month: "月",
		months: {
			jan: "1月",
			feb: "2月",
			mar: "3月",
			apr: "4月",
			may: "5月",
			jun: "6月",
			jul: "7月",
			aug: "8月",
			sep: "9月",
			oct: "10月",
			nov: "11月",
			dec: "12月"
		},
		hour: "时",
		minute: "分",
		second: "秒"
	},
	frame: {
		header: "页眉",
		footer: "页脚"
	},
	pageBreak: { displayName: "分页符" },
	zone: {
		headerTip: "双击编辑页眉",
		footerTip: "双击编辑页脚"
	},
	accessibility: {
		selected: "选中：",
		input: "输入："
	},
	trace: {
		insert: "新增内容",
		delete: "删除内容",
		author: "作者",
		time: "时间",
		unknownAuthor: "未知作者"
	},
	validate: {
		required: "该字段为必填项",
		minLength: "最小长度为 {min}",
		maxLength: "最大长度为 {max}",
		pattern: "格式不正确",
		invalidNumber: "请输入有效数值",
		min: "最小值为 {min}",
		max: "最大值为 {max}",
		integer: "必须为整数",
		precision: "最多 {precision} 位小数",
		minDate: "日期不能早于 {date}",
		maxDate: "日期不能晚于 {date}",
		minChecked: "至少选择 {count} 项",
		maxChecked: "最多选择 {count} 项"
	}
}, La = {
	contextmenu: {
		global: {
			cut: "Cut",
			copy: "Copy",
			paste: "Paste",
			selectAll: "Select all",
			print: "Print"
		},
		control: { delete: "Delete control" },
		hyperlink: {
			delete: "Delete hyperlink",
			cancel: "Cancel hyperlink",
			edit: "Edit hyperlink"
		},
		image: {
			change: "Change image",
			saveAs: "Save as image",
			textWrap: "Text wrap",
			textWrapType: {
				embed: "Embed",
				upDown: "Up down",
				surround: "Surround",
				floatTop: "Float above text",
				floatBottom: "Float below text"
			}
		},
		table: {
			insertRowCol: "Insert row col",
			insertTopRow: "Insert top 1 row",
			insertBottomRow: "Insert bottom 1 row",
			insertLeftCol: "Insert left 1 col",
			insertRightCol: "Insert right 1 col",
			deleteRowCol: "Delete row col",
			deleteRow: "Delete 1 row",
			deleteCol: "Delete 1 col",
			deleteTable: "Delete table",
			mergeCell: "Merge cell",
			mergeCancelCell: "Cancel merge cell",
			autoFitToContent: "AutoFit to contents",
			autoFitToPage: "AutoFit to window",
			verticalAlign: "Vertical align",
			verticalAlignTop: "Top",
			verticalAlignMiddle: "Middle",
			verticalAlignBottom: "Bottom",
			border: "Table border",
			borderAll: "All",
			borderEmpty: "Empty",
			borderDash: "Dash",
			borderExternal: "External",
			borderInternal: "Internal",
			borderTd: "Table cell border",
			borderTdTop: "Top",
			borderTdRight: "Right",
			borderTdBottom: "Bottom",
			borderTdLeft: "Left",
			borderTdForward: "Forward",
			borderTdBack: "Back"
		}
	},
	datePicker: {
		now: "Now",
		confirm: "Confirm",
		return: "Return",
		timeSelect: "Time select",
		weeks: {
			sun: "Sun",
			mon: "Mon",
			tue: "Tue",
			wed: "Wed",
			thu: "Thu",
			fri: "Fri",
			sat: "Sat"
		},
		year: " ",
		month: " ",
		months: {
			jan: "Jan",
			feb: "Feb",
			mar: "Mar",
			apr: "Apr",
			may: "May",
			jun: "Jun",
			jul: "Jul",
			aug: "Aug",
			sep: "Sep",
			oct: "Oct",
			nov: "Nov",
			dec: "Dec"
		},
		hour: "Hour",
		minute: "Minute",
		second: "Second"
	},
	frame: {
		header: "Header",
		footer: "Footer"
	},
	pageBreak: { displayName: "Page Break" },
	zone: {
		headerTip: "Double click to edit header",
		footerTip: "Double click to edit footer"
	},
	accessibility: {
		selected: "Selected: ",
		input: "Input: "
	},
	trace: {
		insert: "Inserted",
		delete: "Deleted",
		author: "Author",
		time: "Time",
		unknownAuthor: "Unknown"
	},
	validate: {
		required: "This field is required",
		minLength: "Minimum length is {min}",
		maxLength: "Maximum length is {max}",
		pattern: "Invalid format",
		invalidNumber: "Please enter a valid number",
		min: "Minimum value is {min}",
		max: "Maximum value is {max}",
		integer: "Must be an integer",
		precision: "Up to {precision} decimal places",
		minDate: "Date cannot be earlier than {date}",
		maxDate: "Date cannot be later than {date}",
		minChecked: "Select at least {count} item(s)",
		maxChecked: "Select at most {count} item(s)"
	}
}, Ra = class {
	currentLocale;
	langMap = /* @__PURE__ */ new Map([["zhCN", Ia], ["en", La]]);
	constructor(e) {
		this.currentLocale = e;
	}
	registerLangMap(e, t) {
		let n = this.langMap.get(e);
		this.langMap.set(e, re(n || Ia, t));
	}
	getLocale() {
		return this.currentLocale;
	}
	setLocale(e) {
		this.currentLocale = e;
	}
	getLang() {
		return this.langMap.get(this.currentLocale) || Ia;
	}
	t(e) {
		let t = e.split("."), n = "", r = this.getLang();
		for (let e = 0; e < t.length; e++) {
			let i = t[e], a = Reflect.get(r, i);
			if (a) n = r = a;
			else return "";
		}
		return n;
	}
}, za = class {
	promiseList;
	constructor() {
		this.promiseList = [];
	}
	add(e) {
		this.promiseList.push(e);
	}
	clearAll() {
		this.promiseList = [];
	}
	allSettled() {
		return Promise.allSettled(this.promiseList);
	}
}, Ba = class {
	draw;
	zone;
	i18n;
	container;
	pageContainer;
	isDisableMouseMove;
	tipContainer;
	tipContent;
	currentMoveZone;
	constructor(e, t) {
		this.draw = e, this.zone = t, this.i18n = e.getI18n(), this.container = e.getContainer(), this.pageContainer = e.getPageContainer();
		let { tipContainer: n, tipContent: r } = this._drawZoneTip();
		this.tipContainer = n, this.tipContent = r, this.isDisableMouseMove = !0, this.currentMoveZone = m.MAIN;
		let i = [], { header: a, footer: o } = e.getOptions();
		a.disabled || i.push(m.HEADER), o.disabled || i.push(m.FOOTER), i.length && this._watchMouseMoveZoneChange(i);
	}
	_watchMouseMoveZoneChange(e) {
		this.pageContainer.addEventListener("mousemove", D((t) => {
			if (!(this.isDisableMouseMove || !this.draw.getIsPagingMode()) && t.offsetY) {
				if (t.target instanceof HTMLCanvasElement) {
					let n = Number(t.target.getAttribute("data-index")), r = this.zone.getZoneByY(t.offsetY, Number.isNaN(n) ? void 0 : n);
					if (!e.includes(r)) {
						this._updateZoneTip(!1);
						return;
					}
					this.currentMoveZone = r, this._updateZoneTip(this.zone.getZone() === m.MAIN && (r === m.HEADER || r === m.FOOTER), t.x, t.y);
				} else this._updateZoneTip(!1);
			}
		}, 250)), this.pageContainer.addEventListener("mouseenter", () => {
			this.isDisableMouseMove = !1;
		}), this.pageContainer.addEventListener("mouseleave", () => {
			this.isDisableMouseMove = !0, this._updateZoneTip(!1);
		});
	}
	_drawZoneTip() {
		let e = document.createElement("div");
		e.classList.add("ce-zone-tip");
		let t = document.createElement("span");
		return e.append(t), this.container.append(e), {
			tipContainer: e,
			tipContent: t
		};
	}
	_updateZoneTip(e, t, n) {
		e ? (this.tipContainer.classList.add("show"), this.tipContainer.style.left = `${t}px`, this.tipContainer.style.top = `${n}px`, this.tipContent.innerText = this.i18n.t(`zone.${this.currentMoveZone === m.HEADER ? "headerTip" : "footerTip"}`)) : this.tipContainer.classList.remove("show");
	}
}, Va = class {
	INDICATOR_PADDING = 2;
	INDICATOR_TITLE_TRANSLATE = [20, 5];
	draw;
	options;
	i18n;
	container;
	currentZone;
	indicatorContainer;
	constructor(e) {
		this.draw = e, this.i18n = e.getI18n(), this.options = e.getOptions(), this.container = e.getContainer(), this.currentZone = m.MAIN, this.indicatorContainer = null, this.options.zone.tipDisabled || new Ba(e, this);
	}
	isHeaderActive() {
		return this.getZone() === m.HEADER;
	}
	isMainActive() {
		return this.getZone() === m.MAIN;
	}
	isFooterActive() {
		return this.getZone() === m.FOOTER;
	}
	getZone() {
		return this.currentZone;
	}
	setZone(e) {
		let { header: t, footer: n } = this.options, r = this.draw.getPageNo();
		e === m.HEADER && (!t.editable || this.draw.getHeader().isDisabled(r)) || e === m.FOOTER && (!n.editable || this.draw.getFooter().isDisabled(r)) || this.currentZone !== e && (this.currentZone = e, this.draw.getRange().clearRange(), this.draw.render({
			isSubmitHistory: !1,
			isSetCursor: !1,
			isCompute: !1
		}), this.drawZoneIndicator(), R(() => {
			let t = this.draw.getListener();
			t.zoneChange && t.zoneChange(e);
			let n = this.draw.getEventBus();
			n.isSubscribe("zoneChange") && n.emit("zoneChange", e);
		}));
	}
	getZoneByY(e, t) {
		let n = this.draw.getHeader(), r = n.isDisabled(t), i = r ? 0 : n.getHeaderTop(t) + n.getHeight(t), a = this.draw.getFooter(), o = a.isDisabled(t), s = t === void 0 ? this.draw.getHeight() : this.draw.getPageSize(t).height, c = o ? s : s - (a.getFooterBottom(t) + a.getHeight(t));
		return !r && e < i ? m.HEADER : !o && e > c ? m.FOOTER : m.MAIN;
	}
	drawZoneIndicator() {
		if (this._clearZoneIndicator(), !this.isHeaderActive() && !this.isFooterActive()) return;
		let { scale: e } = this.options, t = this.isHeaderActive(), [n, r] = this.INDICATOR_TITLE_TRANSLATE, i = this.draw.getPageList();
		this.indicatorContainer = document.createElement("div"), this.indicatorContainer.classList.add("ce-zone-indicator");
		let a = this.draw.getHeader(), o = this.draw.getFooter();
		for (let s = 0; s < i.length; s++) {
			if (t ? a.isDisabled(s) : o.isDisabled(s)) continue;
			let { margins: i, innerWidth: c, height: l } = this.draw.getPageSize(s), { x: u, y: d } = this.draw.getPageOffset(s), f = t ? a.getHeight(s) : o.getHeight(s), p = d + (t ? a.getHeaderTop(s) : l - o.getFooterBottom(s) - f), m = u + i[3] - this.INDICATOR_PADDING, h = u + i[3] + c + this.INDICATOR_PADDING, g = t ? p - this.INDICATOR_PADDING : p + f + this.INDICATOR_PADDING, _ = t ? p + f + this.INDICATOR_PADDING : p - this.INDICATOR_PADDING, v = document.createElement("div");
			v.innerText = this.i18n.t(`frame.${t ? "header" : "footer"}`), v.style.top = `${_}px`, v.style.transform = `translate(${n * e}px, ${r * e}px) scale(${e})`, this.indicatorContainer.append(v);
			let y = document.createElement("span");
			y.classList.add("ce-zone-indicator-border__top"), y.style.top = `${g}px`, y.style.width = `${c}px`, y.style.marginLeft = `${u + i[3]}px`, this.indicatorContainer.append(y);
			let b = document.createElement("span");
			b.classList.add("ce-zone-indicator-border__left"), b.style.top = `${p}px`, b.style.height = `${f}px`, b.style.left = `${m}px`, this.indicatorContainer.append(b);
			let x = document.createElement("span");
			x.classList.add("ce-zone-indicator-border__bottom"), x.style.top = `${_}px`, this.indicatorContainer.append(x);
			let S = document.createElement("span");
			S.classList.add("ce-zone-indicator-border__right"), S.style.top = `${p}px`, S.style.height = `${f}px`, S.style.left = `${h}px`, this.indicatorContainer.append(S);
		}
		this.container.append(this.indicatorContainer);
	}
	_clearZoneIndicator() {
		this.indicatorContainer?.remove(), this.indicatorContainer = null;
	}
}, Ha = class {
	draw;
	position;
	zone;
	options;
	elementList;
	layoutMap;
	constructor(e, t) {
		this.draw = e, this.position = e.getPosition(), this.zone = e.getZone(), this.options = e.getOptions(), this.elementList = t || [], this.layoutMap = /* @__PURE__ */ new Map();
	}
	getRowList() {
		return this._getLayoutByDirection(this.options.paperDirection)[0];
	}
	setElementList(e) {
		this.elementList = e;
	}
	getElementList() {
		return this.elementList;
	}
	getPositionList(e = this.options.paperDirection) {
		return this._getLayoutByDirection(e)[1];
	}
	compute() {
		this.recovery(), this._getLayoutByDirection(this.options.paperDirection);
	}
	recovery() {
		this.layoutMap.clear();
	}
	_getLayoutByDirection(e) {
		let t = this.layoutMap.get(e);
		if (!t) {
			let n = this._computeRowList(e);
			t = [n, []], this.layoutMap.set(e, t), t[1] = this._computePositionList(e, n);
		}
		return t;
	}
	_computeRowList(e) {
		let t = this.draw.getInnerWidth(e);
		return this.draw.computeRowList({
			innerWidth: t,
			elementList: this.elementList
		});
	}
	_computePositionList(e, t) {
		let n = this.getFooterBottom(), r = this.draw.getInnerWidth(e), i = this.draw.getMargins(e)[3], a = this.draw.getHeight(e), o = this.getHeight(void 0, e), s = a - n - o, c = [];
		return this.position.computePageRowPosition({
			positionList: c,
			rowList: t,
			pageNo: 0,
			startRowIndex: 0,
			startIndex: 0,
			startX: i,
			startY: s,
			innerWidth: r,
			zone: m.FOOTER
		}), c;
	}
	getFooterBottom(e) {
		if (this.isDisabled(e)) return 0;
		let { footer: { bottom: t }, scale: n } = this.options;
		return Math.floor(t * n);
	}
	getMaxHeight(e) {
		let { footer: { maxHeightRadio: t } } = this.options, n = this.draw.getHeight(e);
		return Math.floor(n * c[t]);
	}
	getHeight(e, t) {
		if (this.isDisabled(e)) return 0;
		let n = this._resolveDirection(e, t), r = this.getMaxHeight(n), i = this.getRowHeight(n);
		return i > r ? r : i;
	}
	getRowHeight(e = this.options.paperDirection) {
		return this._getLayoutByDirection(e)[0].reduce((e, t) => e + t.height, 0);
	}
	getExtraHeight(e, t) {
		let n = this._resolveDirection(e, t), r = this.draw.getMargins(n), i = this.getHeight(e, n), a = this.getFooterBottom(e) + i - r[2];
		return a <= 0 ? 0 : a;
	}
	_resolveDirection(e, t) {
		return t ?? (e === void 0 ? this.options.paperDirection : this.draw.getPageDirection(e));
	}
	isDisabled(e) {
		return !!(this.options.footer.disabled || e !== void 0 && this.options.footer.disabledPages.includes(e));
	}
	render(e, t) {
		if (this.options.footer.disabledPages.includes(t)) return;
		e.save(), e.globalAlpha = this.zone.isFooterActive() ? 1 : this.options.footer.inactiveAlpha;
		let n = this.draw.getPageDirection(t), r = this.draw.getInnerWidth(n), i = this.getMaxHeight(n), [a, o] = this._getLayoutByDirection(n), s = [], c = 0;
		for (let e = 0; e < a.length; e++) {
			let t = a[e];
			if (c + t.height > i) break;
			s.push(t), c += t.height;
		}
		this.draw.drawRow(e, {
			elementList: this.elementList,
			positionList: o,
			rowList: s,
			pageNo: t,
			startIndex: 0,
			innerWidth: r,
			zone: m.FOOTER
		}), e.restore();
	}
}, Ua = class {
	draw;
	range;
	options;
	UN_COUNT_STYLE_WIDTH = 20;
	MEASURE_BASE_TEXT = "0";
	LIST_GAP = 10;
	LIST_INDENT_WIDTH = 30;
	MAX_LEVEL = 8;
	constructor(e) {
		this.draw = e, this.range = e.getRange(), this.options = e.getOptions();
	}
	setList(e, t) {
		if (this.draw.isReadonly()) return;
		let { startIndex: n, endIndex: r } = this.range.getRange();
		if (!~n && !~r) return;
		let i = this.range.getRangeParagraphElementList();
		if (!i || !i.length) return;
		if (i.find((n) => n.listType === e && n.listStyle === t) || !e) {
			this.unsetList();
			return;
		}
		let a = M();
		i.forEach((n) => {
			n.listId = a, n.listType = e, n.listStyle = t, n.listLevel = 0;
		});
		let o = n === r, s = o ? r : n;
		this.draw.render({
			curIndex: s,
			isSetCursor: o
		});
	}
	unsetList() {
		if (this.draw.isReadonly()) return;
		let { startIndex: e, endIndex: t } = this.range.getRange();
		if (!~e && !~t) return;
		let n = this.range.getRangeParagraphElementList()?.filter((e) => e.listId);
		if (!n || !n.length) return;
		let r = this.draw.getElementList(), i = r[t];
		if (i.listId) {
			let e = t + 1;
			for (; e < r.length;) {
				let t = r[e];
				if (t.value === "​" && !t.listWrap) break;
				if (t.listId !== i.listId) {
					this.draw.spliceElementList(r, e, 0, [{ value: "​" }]);
					break;
				}
				e++;
			}
		}
		n.forEach((e) => {
			delete e.listId, delete e.listType, delete e.listStyle, delete e.listWrap, delete e.listLevel;
		});
		let a = e === t, o = a ? t : e;
		this.draw.render({
			curIndex: o,
			isSetCursor: a
		});
	}
	increaseListLevel() {
		if (this.draw.isReadonly()) return;
		let { startIndex: e, endIndex: t } = this.range.getRange();
		if (!~e && !~t) return;
		let n = this.extractListSegments();
		if (!n.length) return;
		let r = this.draw.getElementList(), i = !1;
		for (let e of n) {
			let t = e[0]?.listLevel ?? 0;
			if (t >= this.MAX_LEVEL) continue;
			let n = t + 1;
			this.applySegmentLevel(e, n, r), i = !0;
		}
		if (!i) return;
		let a = e === t, o = a ? t : e;
		this.draw.render({
			curIndex: o,
			isSetCursor: a
		});
	}
	decreaseListLevel() {
		if (this.draw.isReadonly()) return;
		let { startIndex: e, endIndex: t } = this.range.getRange();
		if (!~e && !~t) return;
		let n = this.extractListSegments();
		if (!n.length) return;
		if (n.some((e) => e[0]?.listId && (e[0].listLevel ?? 0) === 0)) {
			let r = this.draw.getElementList();
			for (let e of n) {
				let t = e[0]?.listId;
				for (let t of e) this.clearListInfo(t);
				t && this.clearPreviousEmptyListItems(r, e[0], t);
			}
			let i = e === t, a = i ? t : e;
			this.draw.render({
				curIndex: a,
				isSetCursor: i
			});
			return;
		}
		let r = this.draw.getElementList(), i = !1;
		for (let e of n) {
			let t = e[0]?.listLevel ?? 0;
			if (t <= 0) continue;
			let n = t - 1;
			this.applySegmentLevel(e, n, r), i = !0;
		}
		if (!i) return;
		let a = e === t, o = a ? t : e;
		this.draw.render({
			curIndex: o,
			isSetCursor: a
		});
	}
	applySegmentLevel(e, t, n) {
		let r = e[0], i = this.findPreviousListId(r, t, n) || M();
		e.forEach((e) => {
			e.listId = i, e.listLevel = t, r.listType && (e.listType = r.listType), r.listStyle && (e.listStyle = r.listStyle);
		});
	}
	findPreviousListId(e, t, n) {
		let r = n.indexOf(e);
		if (~r) for (let i = r - 1; i >= 0; i--) {
			let r = n[i];
			if (r?.listId && !(r.value !== "​" || r.listWrap)) {
				if ((r.listLevel ?? 0) < t) break;
				if (r.listType === e.listType && (r.listLevel ?? 0) === t && this.isParagraphStart(n, i)) return r.listId;
			}
		}
	}
	isParagraphStart(e, t) {
		let n = e[t], r = e[t - 1];
		return !r || r.value === "​" || r.listId !== n.listId || n.value === "​" && !n.listWrap;
	}
	clearListInfo(e) {
		e.listId && (delete e.listId, delete e.listType, delete e.listStyle, delete e.listWrap, delete e.listLevel);
	}
	clearPreviousEmptyListItems(e, t, n) {
		let r = e.indexOf(t);
		for (let t = r - 1; t >= 0; t--) {
			let r = e[t];
			if (r.listId !== n || r.value !== "​" || r.listWrap) break;
			this.clearListInfo(r);
		}
	}
	extractListSegments() {
		let { startIndex: e, endIndex: t } = this.range.getRange();
		if (!~e && !~t) return [];
		let n = this.draw.getElementList();
		if (!n.length) return [];
		let r = Math.min(e, t), i = Math.max(e, t);
		if (!(n[r]?.value === "​" && !n[r]?.listWrap && n[r]?.listId)) for (; r > 0;) {
			let e = n[r - 1];
			if (!e) break;
			if (e.value === "​" && !e.listWrap) {
				e.listId && r--;
				break;
			}
			r--;
		}
		for (; i < n.length - 1;) {
			let e = n[i + 1];
			if (!e || e.value === "​" && !e.listWrap) break;
			i++;
		}
		let a = [], o = [];
		for (let e = r; e <= i; e++) {
			let t = n[e];
			t.value === "​" && !t.listWrap && o.length > 0 && (o.length && a.push(o), o = []), o.push(t);
		}
		return o.length && a.push(o), a.filter((e) => e.some((e) => e.listId));
	}
	computeListStyle(e, t) {
		let n = /* @__PURE__ */ new Map(), r = 0, i = t[r].listId, a = [], o = t.length;
		for (; r < o;) {
			let o = t[r];
			if (i && i === o.listId) a.push(o);
			else if (o.listId && o.listId !== i) {
				if (a.length) {
					let t = this.getListStyleWidth(e, a);
					n.set(i, t);
				}
				i = o.listId, a = i ? [o] : [];
			}
			r++;
		}
		if (a.length) {
			let t = this.getListStyleWidth(e, a);
			n.set(i, t);
		}
		return n;
	}
	findStyledElement(e) {
		let t = e[0];
		for (let n = 1; n < e.length; n++) {
			let r = e[n];
			if (r.font || r.size || r.bold || r.italic) {
				t = r;
				break;
			}
		}
		return t;
	}
	getListFontStyle(e, t) {
		if (this.options.list.inheritStyle) {
			let n = this.findStyledElement(e);
			return this.draw.getElementFont(n, t);
		}
		{
			let { defaultFont: e, defaultSize: n } = this.options;
			return `${n * t}px ${e}`;
		}
	}
	getListStyleWidth(e, t) {
		let { scale: n, checkbox: r } = this.options, i = t[0];
		if (i.listStyle && i.listStyle !== _t.DECIMAL) return i.listStyle === _t.CHECKBOX ? (r.width + this.LIST_GAP) * n : this.UN_COUNT_STYLE_WIDTH * n;
		let a = t.reduce((e, t) => (t.value === "​" && (e += 1), e), 0);
		if (!a) return 0;
		e.save(), e.font = this.getListFontStyle(t, n);
		let o = `${this.MEASURE_BASE_TEXT.repeat(String(a).length - 1 || 1)}${Z.PERIOD}`, s = e.measureText(o);
		return e.restore(), Math.ceil((s.width + this.LIST_GAP) * n);
	}
	drawListStyle(e, t, n) {
		let { elementList: r, offsetX: i, listIndex: a, ascent: o } = t, s = r[0];
		if (s.value !== "​" || s.listWrap) return;
		let c = 0, { defaultTabWidth: l, scale: u } = this.options;
		for (let e = 1; e < r.length && r[e]?.type === H.TAB; e++) c += l * u;
		let { coordinate: { leftTop: [d, f] } } = n, p = s.listLevel ? this.LIST_INDENT_WIDTH * s.listLevel * u : 0, m = d - i + p + c, h = f + o;
		if (s.listStyle === _t.CHECKBOX) {
			let { width: n, height: r, gap: i } = this.options.checkbox, a = {
				...s,
				checkbox: { value: !!s.checkbox?.value },
				metrics: {
					...s.metrics,
					width: (n + i * 2) * u,
					height: r * u
				}
			};
			this.draw.getCheckboxParticle().render({
				ctx: e,
				x: m - i * u,
				y: h,
				index: 0,
				row: {
					...t,
					elementList: [a, ...t.elementList]
				}
			});
		} else {
			let t = "";
			if (s.listType === mt.UL) {
				let e = s.listLevel ?? 0, n = [
					ht.DISC,
					ht.CIRCLE,
					ht.SQUARE
				], r = n[e % n.length];
				t = yt[e === 0 ? s.listStyle || ht.DISC : r] || yt[ht.DISC];
			} else t = `${a + 1}${Z.PERIOD}`;
			if (!t) return;
			e.save(), e.font = this.getListFontStyle(r, u), e.fillText(t, m, h), e.restore();
		}
	}
}, Wa = class e {
	options;
	static WIDTH = 12;
	static HEIGHT = 9;
	static GAP = 3;
	constructor(e) {
		this.options = e.getOptions();
	}
	render(t, n, r, i) {
		let { scale: a, lineBreak: { color: o, lineWidth: s } } = this.options;
		t.save(), t.beginPath();
		let c = i - e.HEIGHT * a / 2, l = r + n.metrics.width;
		t.translate(l, c), t.scale(a, a), t.strokeStyle = o, t.lineWidth = s, t.lineCap = "round", t.lineJoin = "round", t.beginPath(), t.moveTo(8, 0), t.lineTo(12, 0), t.lineTo(12, 6), t.lineTo(3, 6), t.moveTo(3, 6), t.lineTo(6, 3), t.moveTo(3, 6), t.lineTo(6, 9), t.stroke(), t.closePath(), t.restore();
	}
}, Ga = class {
	draw;
	position;
	options;
	elementList;
	rowList;
	positionList;
	constructor(e) {
		this.draw = e, this.position = e.getPosition(), this.options = e.getOptions(), this.elementList = [], this.rowList = [], this.positionList = [];
	}
	_recovery() {
		this.elementList = [], this.rowList = [], this.positionList = [];
	}
	_compute(e) {
		this._computeRowList(), this._computePositionList(e);
	}
	_computeRowList() {
		let e = this.draw.getInnerWidth();
		this.rowList = this.draw.computeRowList({
			innerWidth: e,
			elementList: this.elementList
		});
	}
	_computePositionList(e) {
		let { lineBreak: t, scale: n } = this.options, r = this.draw.getHeader().getExtraHeight(), i = this.draw.getInnerWidth(), a = this.draw.getMargins(), o = a[3];
		t.disabled || (o += (Wa.WIDTH + Wa.GAP) * n);
		let s = e?.startY || a[0] + r;
		this.position.computePageRowPosition({
			positionList: this.positionList,
			rowList: this.rowList,
			pageNo: 0,
			startRowIndex: 0,
			startIndex: 0,
			startX: o,
			startY: s,
			innerWidth: i
		});
	}
	render(e, t) {
		let { placeholder: n = this.options.placeholder } = t || {}, { data: r, font: i, size: a, color: o, opacity: s } = n;
		this._recovery(), this.elementList = [{
			value: r,
			font: i,
			size: a,
			color: o
		}], yn(this.elementList, {
			editorOptions: this.options,
			isForceCompensation: !0
		}), this._compute(t);
		let c = this.draw.getInnerWidth();
		e.save(), e.globalAlpha = s, this.draw.drawRow(e, {
			elementList: this.elementList,
			positionList: this.positionList,
			rowList: this.rowList,
			pageNo: 0,
			startIndex: 0,
			innerWidth: c,
			isDrawLineBreak: !1
		}), e.restore();
	}
}, Ka = class {
	draw;
	options;
	range;
	fillRectMap;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.range = e.getRange(), this.fillRectMap = /* @__PURE__ */ new Map();
	}
	setGroup() {
		if (this.draw.getZone().getZone() !== m.MAIN) return null;
		let e = this.range.getSelection();
		if (!e) return null;
		let t = M();
		return e.forEach((e) => {
			Array.isArray(e.groupIds) || (e.groupIds = []), e.groupIds.push(t);
		}), this.draw.render({
			isSetCursor: !1,
			isCompute: !1
		}), t;
	}
	getElementListByGroupId(e, t) {
		let n = [];
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			if (i.type === H.TABLE) {
				let e = i.trList;
				for (let r = 0; r < e.length; r++) {
					let i = e[r];
					for (let e = 0; e < i.tdList.length; e++) {
						let r = i.tdList[e], a = this.getElementListByGroupId(r.value, t);
						if (a.length) return n.push(...a), n;
					}
				}
			}
			if (i?.groupIds?.includes(t) && (n.push(i), !e[r + 1]?.groupIds?.includes(t))) break;
		}
		return n;
	}
	deleteGroup(e) {
		let t = this.draw.getOriginalMainElementList(), n = this.getElementListByGroupId(t, e);
		if (n.length) {
			for (let t = 0; t < n.length; t++) {
				let r = n[t], i = r.groupIds, a = i.findIndex((t) => t === e);
				i.splice(a, 1), i.length || delete r.groupIds;
			}
			this.draw.render({
				isSetCursor: !1,
				isCompute: !1
			});
		}
	}
	getContextByGroupId(e, t) {
		for (let n = 0; n < e.length; n++) {
			let r = e[n];
			if (r.type === H.TABLE) {
				let e = r.trList;
				for (let i = 0; i < e.length; i++) {
					let a = e[i];
					for (let e = 0; e < a.tdList.length; e++) {
						let o = a.tdList[e], s = this.getContextByGroupId(o.value, t);
						if (s) return {
							...s,
							isTable: !0,
							index: n,
							trIndex: i,
							tdIndex: e,
							tdId: o.id,
							trId: a.id,
							tableId: r.tableId
						};
					}
				}
			}
			let i = e[n + 1];
			if (r.groupIds?.includes(t) && !i?.groupIds?.includes(t)) return {
				isTable: !1,
				startIndex: n,
				endIndex: n
			};
		}
		return null;
	}
	clearFillInfo() {
		this.fillRectMap.clear();
	}
	recordFillInfo(e, t, n, r, i) {
		let a = e.groupIds;
		if (a) for (let e of a) {
			let a = this.fillRectMap.get(e);
			a ? a.width += r : this.fillRectMap.set(e, {
				x: t,
				y: n,
				width: r,
				height: i
			});
		}
	}
	render(e) {
		if (!this.fillRectMap.size) return;
		let t = this.range.getRange(), n = this.draw.getElementList()[t.endIndex]?.groupIds, { group: { backgroundColor: r, opacity: i, activeOpacity: a, activeBackgroundColor: o } } = this.options;
		e.save(), this.fillRectMap.forEach((t, s) => {
			let { x: c, y: l, width: u, height: d } = t;
			n?.includes(s) ? (e.globalAlpha = a, e.fillStyle = o) : (e.globalAlpha = i, e.fillStyle = r), e.fillRect(c, l, u, d);
		}), e.restore(), this.clearFillInfo();
	}
}, qa = class {
	options;
	constructor(e) {
		this.options = e.getOptions();
	}
	render(e, t, n, r) {
		let { scale: i, whiteSpace: { color: a, radius: o } } = this.options, s = t.metrics;
		e.save(), e.fillStyle = a, e.beginPath(), e.arc(n + s.width / 2, r, o * i, 0, Math.PI * 2), e.fill(), e.closePath(), e.restore();
	}
}, Ja = class {
	draw;
	eventBus;
	pageContainer;
	constructor(e) {
		this.draw = e, this.eventBus = this.draw.getEventBus(), this.pageContainer = this.draw.getPageContainer(), this.pageContainer.addEventListener("mousemove", this._mousemove.bind(this)), this.pageContainer.addEventListener("mouseenter", this._mouseenter.bind(this)), this.pageContainer.addEventListener("mouseleave", this._mouseleave.bind(this)), this.pageContainer.addEventListener("mousedown", this._mousedown.bind(this)), this.pageContainer.addEventListener("mouseup", this._mouseup.bind(this)), this.pageContainer.addEventListener("click", this._click.bind(this));
	}
	_mousemove(e) {
		this.eventBus.isSubscribe("mousemove") && this.eventBus.emit("mousemove", e);
	}
	_mouseenter(e) {
		this.eventBus.isSubscribe("mouseenter") && this.eventBus.emit("mouseenter", e);
	}
	_mouseleave(e) {
		this.eventBus.isSubscribe("mouseleave") && this.eventBus.emit("mouseleave", e);
	}
	_mousedown(e) {
		this.eventBus.isSubscribe("mousedown") && this.eventBus.emit("mousedown", e);
	}
	_mouseup(e) {
		this.eventBus.isSubscribe("mouseup") && this.eventBus.emit("mouseup", e);
	}
	_click(e) {
		this.eventBus.isSubscribe("click") && this.eventBus.emit("click", e);
	}
}, Ya = class {
	draw;
	options;
	constructor(e) {
		this.draw = e, this.options = e.getOptions();
	}
	render(e, t) {
		let { scale: n, lineNumber: { color: r, size: i, font: a, right: o, type: s } } = this.options, c = this.draw.getTextParticle(), { margins: l } = this.draw.getPageSize(t), u = this.draw.getPosition().getOriginalMainPositionList(), d = this.draw.getPageRowList()[t];
		e.save(), e.fillStyle = r, e.font = `${i * n}px ${a}`;
		for (let t = 0; t < d.length; t++) {
			let r = d[t], { coordinate: { leftBottom: i } } = r.fragmentPosition || u[r.startIndex], a = s === en.PAGE ? t + 1 : r.rowIndex + 1, f = c.measureText(e, { value: `${a}` }), p = l[3] - (f.width + o) * n, m = i[1] - f.actualBoundingBoxAscent * n;
			e.fillText(`${a}`, p, m);
		}
		e.restore();
	}
}, Xa = class {
	draw;
	header;
	footer;
	options;
	constructor(e) {
		this.draw = e, this.header = e.getHeader(), this.footer = e.getFooter(), this.options = e.getOptions();
	}
	render(e, t) {
		let { scale: n, pageBorder: { color: r, lineWidth: i, padding: a } } = this.options;
		e.save(), e.translate(.5, .5), e.strokeStyle = r, e.lineWidth = i * n;
		let { margins: o, innerWidth: s, height: c } = this.draw.getPageSize(t), l = o[3] - a[3] * n, u = o[0] + this.header.getExtraHeight(t) - a[0] * n, d = s + (a[1] + a[3]) * n, f = c - u - this.footer.getExtraHeight(t) - o[2] + a[2] * n;
		e.rect(l, u, d, f), e.stroke(), e.restore();
	}
};
//#endregion
//#region src/editor/core/actuator/handlers/positionContextChange.ts
function Za(e, t) {
	let { value: n, oldValue: r } = t;
	r.isTable && !n.isTable && e.getTableTool().dispose();
}
//#endregion
//#region src/editor/core/actuator/Actuator.ts
var Qa = class {
	draw;
	eventBus;
	constructor(e) {
		this.draw = e, this.eventBus = e.getEventBus(), this.execute();
	}
	execute() {
		this.eventBus.on("positionContextChange", (e) => {
			Za(this.draw, e);
		});
	}
}, $a = class {
	draw;
	range;
	position;
	tableTool;
	tableParticle;
	options;
	constructor(e) {
		this.draw = e, this.range = e.getRange(), this.position = e.getPosition(), this.tableTool = e.getTableTool(), this.tableParticle = e.getTableParticle(), this.options = e.getOptions();
	}
	insertTable(e, t) {
		let { startIndex: n, endIndex: r } = this.range.getRange();
		if (!~n && !~r) return;
		let { defaultTrMinHeight: i } = this.options.table, a = this.draw.getElementList(), o = 0;
		if (a[n]?.listId) {
			let { rowIndex: e } = this.position.getPositionList()[n];
			o = this.draw.getRowList()[e]?.offsetX || 0;
		}
		let s = this.draw.getContextInnerWidth() - o, c = [], l = s / t;
		for (let e = 0; e < t; e++) c.push({ width: l });
		let u = [];
		for (let n = 0; n < e; n++) {
			let e = [], n = {
				height: i,
				tdList: e
			};
			for (let n = 0; n < t; n++) e.push({
				colspan: 1,
				rowspan: 1,
				value: []
			});
			u.push(n);
		}
		let d = {
			type: H.TABLE,
			value: "",
			colgroup: c,
			trList: u
		};
		yn([d], { editorOptions: this.options }), kn(a, [d], n, { editorOptions: this.options });
		let f = n + 1;
		n !== r && this.draw.deleteElementList(a, f, r - n), this.draw.getTraceParticle().markElementListInserted([d]), this.draw.spliceElementList(a, f, 0, [d]), this.range.setRange(f, f), this.draw.render({
			curIndex: f,
			isSetCursor: !1
		});
	}
	insertTableTopRow() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t, trIndex: n, tableId: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = a[n];
		if (o.tdList.length < i.colgroup.length) {
			let e = o.tdList[0].rowIndex;
			for (let t = 0; t < n; t++) {
				let n = a[t];
				for (let t = 0; t < n.tdList.length; t++) {
					let r = n.tdList[t];
					r.rowspan > 1 && r.rowIndex + r.rowspan >= e + 1 && (r.rowspan += 1);
				}
			}
		}
		let s = M(), c = {
			height: o.height,
			id: s,
			tdList: []
		};
		for (let e = 0; e < o.tdList.length; e++) {
			let t = o.tdList[e], n = M();
			c.tdList.push({
				id: n,
				rowspan: 1,
				colspan: t.colspan,
				value: [{
					value: "​",
					size: 16,
					tableId: r,
					trId: s,
					tdId: n
				}]
			});
		}
		a.splice(n, 0, c), this.position.setPositionContext({
			isTable: !0,
			index: t,
			trIndex: n,
			tdIndex: 0,
			tdId: c.tdList[0].id,
			trId: c.id,
			tableId: r
		}), this.range.setRange(0, 0), this.draw.render({ curIndex: 0 }), this.tableTool.render();
	}
	insertTableBottomRow() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t, trIndex: n, tableId: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = a[n], s = a.length - 1 === n ? o : a[n + 1];
		if (s.tdList.length < i.colgroup.length) {
			let e = s.tdList[0].rowIndex;
			for (let t = 0; t < n + 1; t++) {
				let n = a[t];
				for (let t = 0; t < n.tdList.length; t++) {
					let r = n.tdList[t];
					r.rowspan > 1 && r.rowIndex + r.rowspan >= e + 1 && (r.rowspan += 1);
				}
			}
		}
		let c = M(), l = {
			height: s.height,
			id: c,
			tdList: []
		};
		for (let e = 0; e < s.tdList.length; e++) {
			let t = s.tdList[e], n = M();
			l.tdList.push({
				id: n,
				rowspan: 1,
				colspan: t.colspan,
				value: [{
					value: "​",
					size: 16,
					tableId: r,
					trId: c,
					tdId: n
				}]
			});
		}
		a.splice(n + 1, 0, l), this.position.setPositionContext({
			isTable: !0,
			index: t,
			trIndex: n + 1,
			tdIndex: 0,
			tdId: l.tdList[0].id,
			trId: l.id,
			tableId: i.id
		}), this.range.setRange(0, 0), this.draw.render({ curIndex: 0 });
	}
	adjustColWidth(e) {
		if (e.type !== H.TABLE) return;
		let { defaultColMinWidth: t, overflow: n } = this.options.table;
		if (n) return;
		let r = e.colgroup, i = r.reduce((e, t) => e + t.width, 0), a = this.draw.getOriginalInnerWidth();
		if (i > a) {
			let e = r.filter((e) => e.width > t), n = (i - a) / e.length;
			for (let e = 0; e < r.length; e++) {
				let i = r[e];
				i.width - n >= t && (i.width -= n);
			}
		}
	}
	insertTableLeftCol() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t, tdIndex: n, tableId: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = n;
		for (let e = 0; e < a.length; e++) {
			let t = a[e], n = M();
			t.tdList.splice(o, 0, {
				id: n,
				rowspan: 1,
				colspan: 1,
				value: [{
					value: "​",
					size: 16,
					tableId: r,
					trId: t.id,
					tdId: n
				}]
			});
		}
		let { defaultColMinWidth: s } = this.options.table;
		i.colgroup.splice(o, 0, { width: s }), this.adjustColWidth(i), this.position.setPositionContext({
			isTable: !0,
			index: t,
			trIndex: 0,
			tdIndex: o,
			tdId: a[0].tdList[o].id,
			trId: a[0].id,
			tableId: r
		}), this.range.setRange(0, 0), this.draw.render({ curIndex: 0 }), this.tableTool.render();
	}
	insertTableRightCol() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t, tdIndex: n, tableId: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = n + 1;
		for (let e = 0; e < a.length; e++) {
			let t = a[e], n = M();
			t.tdList.splice(o, 0, {
				id: n,
				rowspan: 1,
				colspan: 1,
				value: [{
					value: "​",
					size: 16,
					tableId: r,
					trId: t.id,
					tdId: n
				}]
			});
		}
		let { defaultColMinWidth: s } = this.options.table;
		i.colgroup.splice(o, 0, { width: s }), this.adjustColWidth(i), this.position.setPositionContext({
			isTable: !0,
			index: t,
			trIndex: 0,
			tdIndex: o,
			tdId: a[0].tdList[o].id,
			trId: a[0].id,
			tableId: i.id
		}), this.range.setRange(0, 0), this.draw.render({ curIndex: 0 });
	}
	deleteTableRow() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t, trIndex: n, tdIndex: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = a[n], s = o.tdList[r].rowIndex;
		if (a.length <= 1) {
			this.deleteTable();
			return;
		}
		for (let e = 0; e < s; e++) {
			let t = a[e].tdList;
			for (let e = 0; e < t.length; e++) {
				let n = t[e];
				n.rowIndex + n.rowspan > s && n.rowspan--;
			}
		}
		for (let e = 0; e < o.tdList.length; e++) {
			let t = o.tdList[e];
			if (t.rowspan > 1) {
				let r = M(), o = a[n + 1];
				o.tdList.splice(e, 0, {
					id: r,
					rowspan: t.rowspan - 1,
					colspan: t.colspan,
					value: [{
						value: "​",
						size: 16,
						tableId: i.id,
						trId: o.id,
						tdId: r
					}]
				});
			}
		}
		a.splice(n, 1), this.position.setPositionContext({ isTable: !1 }), this.range.clearRange(), this.draw.render({ curIndex: e.index }), this.tableTool.dispose();
	}
	deleteTableCol() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t, tdIndex: n, trIndex: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = a[r].tdList[n].colIndex;
		if (!a.find((e) => e.tdList.length > 1)) {
			this.deleteTable();
			return;
		}
		for (let e = 0; e < a.length; e++) {
			let t = a[e];
			for (let e = 0; e < t.tdList.length; e++) {
				let n = t.tdList[e];
				n.colIndex <= o && n.colIndex + n.colspan > o && (n.colspan > 1 ? n.colspan-- : t.tdList.splice(e, 1));
			}
		}
		i.colgroup?.splice(o, 1), this.position.setPositionContext({ isTable: !1 }), this.range.setRange(0, 0), this.draw.render({ curIndex: e.index }), this.tableTool.dispose();
	}
	deleteTable() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let t = this.draw.getOriginalElementList(), n = e.index;
		t.splice(n, 1);
		let r = n - 1;
		this.position.setPositionContext({
			isTable: !1,
			index: r
		}), this.range.setRange(r, r), this.draw.render({ curIndex: r }), this.tableTool.dispose();
	}
	mergeTableCell() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { isCrossRowCol: t, startTdIndex: n, endTdIndex: r, startTrIndex: i, endTrIndex: a } = this.range.getRange();
		if (!t) return;
		let o = this.draw.getOriginalElementList(), s = this.position.getTableElementByContext(o, e), c = s.trList, l = c[i].tdList[n], u = c[a].tdList[r];
		(l.x > u.x || l.y > u.y) && ([l, u] = [u, l]);
		let d = l.colIndex, f = u.colIndex + (u.colspan - 1), p = l.rowIndex, m = u.rowIndex + (u.rowspan - 1), h = [];
		for (let e = 0; e < c.length; e++) {
			let t = c[e], n = [];
			for (let e = 0; e < t.tdList.length; e++) {
				let r = t.tdList[e], i = r.colIndex, a = r.rowIndex;
				i >= d && i <= f && a >= p && a <= m && n.push(r);
			}
			n.length && h.push(n);
		}
		if (!h.length) return;
		let g = h[h.length - 1], _ = h[0][0], v = g[g.length - 1], y = _.x, b = _.y, x = v.x + v.width, S = v.y + v.height;
		for (let e = 0; e < h.length; e++) {
			let t = h[e];
			for (let e = 0; e < t.length; e++) {
				let n = t[e], r = n.x, i = n.y, a = r + n.width, o = i + n.height;
				if (y > r || b > i || x < a || S < o) return;
			}
		}
		let C = [], w = h[0][0], T = w.value[0];
		for (let e = 0; e < h.length; e++) {
			let t = h[e];
			for (let n = 0; n < t.length; n++) {
				let r = t[n];
				if (e !== 0 || n !== 0) {
					C.push(r.id);
					let e = r.value.length > 1 ? 0 : 1;
					for (let t = e; t < r.value.length; t++) {
						let e = r.value[t];
						B(Ne, T, e), w.value.push(e);
					}
				}
				e === 0 && n !== 0 && (w.colspan += r.colspan), e !== 0 && w.colIndex === r.colIndex && (w.rowspan += r.rowspan);
			}
		}
		for (let e = 0; e < c.length; e++) {
			let t = c[e], n = 0;
			for (; n < t.tdList.length;) {
				let e = t.tdList[n];
				C.includes(e.id) && (t.tdList.splice(n, 1), n--), n++;
			}
		}
		this.position.setPositionContext(this.position.buildTablePositionContext(e, s, w.trIndex, w.tdIndex));
		let E = w.value.length - 1;
		this.range.setRange(E, E), this.draw.render(), this.tableTool.render();
	}
	cancelMergeTableCell() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { tdIndex: t, trIndex: n } = e, r = this.draw.getOriginalElementList(), i = this.position.getTableElementByContext(r, e), a = i.trList, o = a[n], s = o.tdList[t];
		if (s.rowspan === 1 && s.colspan === 1) return;
		let c = s.colspan;
		if (s.colspan > 1) {
			for (let e = 1; e < s.colspan; e++) {
				let n = M();
				o.tdList.splice(t + e, 0, {
					id: n,
					rowspan: 1,
					colspan: 1,
					value: [{
						value: "​",
						size: 16,
						tableId: i.id,
						trId: o.id,
						tdId: n
					}]
				});
			}
			s.colspan = 1;
		}
		if (s.rowspan > 1) {
			for (let e = 1; e < s.rowspan; e++) {
				let t = a[n + e];
				for (let e = 0; e < c; e++) {
					let e = M();
					t.tdList.splice(s.colIndex, 0, {
						id: e,
						rowspan: 1,
						colspan: 1,
						value: [{
							value: "​",
							size: 16,
							tableId: i.id,
							trId: t.id,
							tdId: e
						}]
					});
				}
			}
			s.rowspan = 1;
		}
		let l = s.value.length - 1;
		this.range.setRange(l, l), this.draw.render(), this.tableTool.render();
	}
	splitVerticalTableCell() {
		let e = this.position.getPositionContext();
		if (!e.isTable || this.range.getRange().isCrossRowCol) return;
		let { index: t, tdIndex: n, trIndex: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = a[r], s = o.tdList[n];
		i.colgroup.splice(n + 1, 0, { width: this.options.table.defaultColMinWidth });
		for (let e = 0; e < a.length; e++) {
			let t = a[e], n = 0;
			for (; n < t.tdList.length;) {
				let e = t.tdList[n];
				if (e.rowIndex !== s.rowIndex) e.colIndex <= s.colIndex && e.colIndex + e.colspan > s.colIndex && e.colspan++;
				else if (e.id === s.id) {
					let e = M();
					o.tdList.splice(n + s.colspan, 0, {
						id: e,
						rowspan: s.rowspan,
						colspan: 1,
						value: [{
							value: "​",
							size: 16,
							tableId: i.id,
							trId: t.id,
							tdId: e
						}]
					}), n++;
				}
				n++;
			}
		}
		this.draw.render(), this.tableTool.render();
	}
	splitHorizontalTableCell() {
		let e = this.position.getPositionContext();
		if (!e.isTable || this.range.getRange().isCrossRowCol) return;
		let { index: t, tdIndex: n, trIndex: r } = e, i = this.draw.getOriginalElementList()[t], a = i.trList, o = a[r].tdList[n], s = -1, c = 0;
		for (; c < a.length;) {
			if (c === s) {
				c++;
				continue;
			}
			let e = a[c], t = 0;
			for (; t < e.tdList.length;) {
				let n = e.tdList[t];
				if (n.id === o.id) {
					let e = M(), t = M();
					a.splice(c + o.rowspan, 0, {
						id: e,
						height: this.options.table.defaultTrMinHeight,
						tdList: [{
							id: t,
							rowspan: 1,
							colspan: o.colspan,
							value: [{
								value: "​",
								size: 16,
								tableId: i.id,
								trId: e,
								tdId: t
							}]
						}]
					}), s = c + o.rowspan;
				} else n.rowIndex >= o.rowIndex && n.rowIndex < o.rowIndex + o.rowspan && n.rowIndex + n.rowspan >= o.rowIndex + o.rowspan && n.rowspan++;
				t++;
			}
			c++;
		}
		this.draw.render(), this.tableTool.render();
	}
	tableTdVerticalAlign(e) {
		let t = this.tableParticle.getRangeRowCol();
		if (!t) return;
		for (let n = 0; n < t.length; n++) {
			let r = t[n];
			for (let t = 0; t < r.length; t++) {
				let n = r[t];
				!n || n.verticalAlign === e || !n.verticalAlign && e === Y.TOP || (n.verticalAlign = e);
			}
		}
		let { endIndex: n } = this.range.getRange();
		this.draw.render({ curIndex: n });
	}
	tableBorderType(e) {
		let t = this.position.getPositionContext();
		if (!t.isTable) return;
		let { index: n } = t, r = this.draw.getOriginalElementList()[n];
		if (!r.borderType && e === kt.ALL || r.borderType === e) return;
		r.borderType = e;
		let { endIndex: i } = this.range.getRange();
		this.draw.render({ curIndex: i });
	}
	tableBorderColor(e) {
		let t = this.position.getPositionContext();
		if (!t.isTable) return;
		let { index: n } = t, r = this.draw.getOriginalElementList()[n];
		if (!r.borderColor && e === this.options.table.defaultBorderColor || r.borderColor === e) return;
		r.borderColor = e;
		let { endIndex: i } = this.range.getRange();
		this.draw.render({
			curIndex: i,
			isCompute: !1
		});
	}
	tableTdBorderType(e) {
		let t = this.tableParticle.getRangeRowCol();
		if (!t) return;
		let n = t.flat(), r = n.some((t) => !t.borderTypes?.includes(e));
		n.forEach((t) => {
			t.borderTypes ||= [];
			let n = t.borderTypes.findIndex((t) => t === e);
			r ? ~n || t.borderTypes.push(e) : ~n && t.borderTypes.splice(n, 1), t.borderTypes.length || delete t.borderTypes;
		});
		let { endIndex: i } = this.range.getRange();
		this.draw.render({ curIndex: i });
	}
	tableTdSlashType(e) {
		let t = this.tableParticle.getRangeRowCol();
		if (!t) return;
		let n = t.flat(), r = n.some((t) => !t.slashTypes?.includes(e));
		n.forEach((t) => {
			t.slashTypes ||= [];
			let n = t.slashTypes.findIndex((t) => t === e);
			r ? ~n || t.slashTypes.push(e) : ~n && t.slashTypes.splice(n, 1), t.slashTypes.length || delete t.slashTypes;
		});
		let { endIndex: i } = this.range.getRange();
		this.draw.render({ curIndex: i });
	}
	tableTdBackgroundColor(e) {
		let t = this.tableParticle.getRangeRowCol();
		if (!t) return;
		for (let n = 0; n < t.length; n++) {
			let r = t[n];
			for (let t = 0; t < r.length; t++) {
				let n = r[t];
				n.backgroundColor = e;
			}
		}
		let { endIndex: n } = this.range.getRange();
		this.range.setRange(n, n), this.draw.render({ isCompute: !1 });
	}
	_measureTdContentWidth(e) {
		let t = document.createElement("canvas").getContext("2d"), n = this.draw.getTextParticle(), r = 0, i = 0;
		for (let a = 0; a < e.value.length; a++) {
			let o = e.value[a];
			if (o.value === "​") {
				r = Math.max(r, i), i = 0;
				continue;
			}
			o.type && o.type !== H.TEXT || (t.font = this.draw.getElementFont(o), i += n.measureText(t, o).width);
		}
		return Math.max(r, i);
	}
	tableAutoFitToContent() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t } = e, n = this.draw.getOriginalElementList()[t];
		if (n?.type !== H.TABLE) return;
		let { defaultColMinWidth: r, tdPadding: i, overflow: a } = this.options.table, o = i[1] + i[3], s = n.colgroup, c = s.map(() => 0);
		for (let e = 0; e < n.trList.length; e++) {
			let t = n.trList[e].tdList;
			for (let e = 0; e < t.length; e++) {
				let n = t[e];
				if (n.colspan > 1) continue;
				let r = n.colIndex, i = this._measureTdContentWidth(n) + o;
				i > c[r] && (c[r] = i);
			}
		}
		for (let e = 0; e < s.length; e++) c[e] && (s[e].width = Math.max(r, c[e]));
		a || (ga(s, this.draw.getOriginalInnerWidth(), r), n.translateX = 0);
		let { endIndex: l } = this.range.getRange();
		this.draw.render({ curIndex: l }), this.tableTool.render();
	}
	tableAutoFitToPage() {
		let e = this.position.getPositionContext();
		if (!e.isTable) return;
		let { index: t } = e, n = this.draw.getOriginalElementList()[t];
		if (n?.type !== H.TABLE) return;
		_a(n.colgroup, this.draw.getOriginalInnerWidth()), n.translateX = 0;
		let { endIndex: r } = this.range.getRange();
		this.draw.render({ curIndex: r }), this.tableTool.render();
	}
	tableSelectAll() {
		let { index: e, tableId: t, isTable: n } = this.position.getPositionContext();
		if (!n || !t) return;
		let { startIndex: r, endIndex: i } = this.range.getRange(), a = this.draw.getOriginalElementList()[e].trList, o = a.length - 1, s = a[o].tdList.length - 1;
		this.range.replaceRange({
			startIndex: r,
			endIndex: i,
			tableId: t,
			startTdIndex: 0,
			endTdIndex: s,
			startTrIndex: 0,
			endTrIndex: o
		}), this.draw.render({
			isSetCursor: !1,
			isCompute: !1,
			isSubmitHistory: !1
		});
	}
}, eo;
(function(e) {
	e.EDIT = "edit", e.READONLY = "readonly", e.FORM = "form";
})(eo ||= {});
//#endregion
//#region src/editor/core/draw/interactive/Area.ts
var to = class {
	draw;
	zone;
	range;
	position;
	options;
	areaInfoMap = /* @__PURE__ */ new Map();
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.zone = e.getZone(), this.range = e.getRange(), this.position = e.getPosition();
	}
	getAreaInfo() {
		return this.areaInfoMap;
	}
	getActiveAreaId() {
		if (!this.areaInfoMap.size) return null;
		let { startIndex: e } = this.range.getRange();
		return this.draw.getElementList()[e]?.areaId || null;
	}
	getActiveAreaInfo() {
		let e = this.getActiveAreaId();
		return e && this.areaInfoMap.get(e) || null;
	}
	isReadonly() {
		let e = this.getActiveAreaInfo();
		if (!e?.area) return !1;
		switch (e.area.mode) {
			case eo.EDIT: return !1;
			case eo.READONLY: return !0;
			case eo.FORM: return !this.draw.getControl().getIsRangeWithinControl();
			default: return !1;
		}
	}
	insertArea(e) {
		let { id: t, value: n, area: r, position: a, range: o } = e;
		if (this.zone.getZone() !== m.MAIN && this.zone.setZone(m.MAIN), o && !this.getActiveAreaId()) {
			let { startIndex: e, endIndex: t } = o, n = this.draw.getMainElementList();
			if (!n[e] || !n[t]) return null;
			this.range.setRange(o.startIndex, o.endIndex);
		} else if (a === i.BEFORE) this.range.setRange(0, 0);
		else {
			let e = this.draw.getMainElementList().length - 1;
			this.range.setRange(e, e);
		}
		let s = t || M();
		return this.draw.insertElementList([{
			type: H.AREA,
			value: "",
			areaId: s,
			valueList: n,
			area: k(r)
		}]), s;
	}
	render(e, t) {
		if (!this.areaInfoMap.size) return;
		e.save();
		let n = this.draw.getMargins(), r = this.draw.getInnerWidth();
		for (let i of this.areaInfoMap) {
			let { area: a, positionList: o } = i[1];
			if (a?.hide && !this.draw.isAreaHideDisabled() || !a?.backgroundColor && !a?.borderColor && !a?.placeholder) continue;
			let s = o.filter((e) => e.pageNo === t);
			if (!s.length) continue;
			e.translate(.5, .5);
			let c = s[0], l = s[s.length - 1], u = i[1].tableCell, d = !!u, f = this.draw.getTdPadding(), p = d ? u.tablePosition.coordinate.leftTop[0] + u.td.x * this.options.scale + f[3] : n[3], m = Math.ceil(c.coordinate.leftTop[1]), h = Math.ceil(l.coordinate.rightBottom[1] - m), g = d ? u.td.width * this.options.scale - f[1] - f[3] : r;
			a.backgroundColor && (e.fillStyle = a.backgroundColor, e.fillRect(p, m, g, h)), a.borderColor && (e.strokeStyle = a.borderColor, e.strokeRect(p, m, g, h)), a.placeholder && o.length <= 1 && new Ga(this.draw).render(e, {
				placeholder: {
					...Kt,
					...a.placeholder
				},
				startY: c.coordinate.leftTop[1]
			}), e.translate(-.5, -.5);
		}
		e.restore();
	}
	compute() {
		this.areaInfoMap.clear();
		let e = this.draw.getOriginalMainElementList(), t = this.position.getOriginalMainPositionList();
		this.computeAreaInfo(e, t, e);
	}
	computeAreaInfo(e, t = [], n, r, i) {
		for (let a = 0; a < e.length; a++) {
			let o = e[a], s = o.areaId, c = t[a];
			if (s && s !== r) {
				let e = this.areaInfoMap.get(s);
				e ? (e.elementList.push(o), c && e.positionList.push(c)) : this.areaInfoMap.set(s, {
					id: s,
					area: o.area,
					elementList: [o],
					positionList: c ? [c] : [],
					sourceElementList: n,
					tableCell: i
				});
			}
			o.type === H.TABLE && o.trList && this.computeTableAreaInfo(o, c, s);
		}
	}
	computeTableAreaInfo(e, t, n) {
		let r = e.trList;
		for (let e = 0; e < r.length; e++) {
			let i = r[e];
			for (let e = 0; e < i.tdList.length; e++) {
				let r = i.tdList[e];
				this.computeAreaInfo(r.value, r.positionList, r.value, n, t ? {
					td: r,
					tablePosition: t
				} : void 0);
			}
		}
	}
	getAreaValue(e = {}) {
		let t = e.id || this.getActiveAreaId();
		if (!t) return null;
		let n = this.areaInfoMap.get(t);
		return n ? {
			area: n.area,
			id: n.id,
			startPageNo: n.positionList[0].pageNo,
			endPageNo: n.positionList[n.positionList.length - 1].pageNo,
			value: X(gn(n.elementList), { isClone: !1 })
		} : null;
	}
	getContextByAreaId(e, t) {
		let n = this.draw.getOriginalMainElementList();
		for (let r = 0; r < n.length; r++) {
			let a = n[r];
			if (t?.position === i.OUTER_BEFORE) {
				if (n[r + 1]?.areaId !== e) continue;
			} else if (t?.position === i.AFTER) {
				if (a.areaId !== e || n[r + 1]?.areaId === e) continue;
			} else if (t?.position === i.OUTER_AFTER) {
				if (a.areaId === e || n[r - 1]?.areaId !== e) continue;
			} else if (a.areaId !== e) continue;
			let o = this.position.getOriginalMainPositionList();
			return {
				range: {
					startIndex: r,
					endIndex: r
				},
				elementPosition: o[r]
			};
		}
		return null;
	}
	setAreaProperties(e) {
		let t = e.id || this.getActiveAreaId();
		if (!t) return;
		let n = this.areaInfoMap.get(t);
		if (!n) return;
		n.area ||= {};
		let r = !1, i = ["top", "hide"];
		Object.entries(e.properties).forEach(([e, t]) => {
			if (de(t)) return;
			let a = e;
			n.area[a] = t, i.includes(a) && (r = !0);
		}), this.draw.render({
			isCompute: r,
			isSetCursor: !1
		});
	}
	setAreaValue(e) {
		let t = e.id || this.getActiveAreaId();
		if (!t) return;
		let n = this.areaInfoMap.get(t);
		if (!n) return;
		let { positionList: r } = n, i = n.sourceElementList, a = e.value;
		yn([{
			type: H.AREA,
			value: "",
			valueList: a,
			areaId: n.id,
			area: n.area
		}], { editorOptions: this.options });
		let o = r[0].index;
		this.draw.deleteElementList(i, o, r.length, { isIgnoreDeletedRule: !0 }), this.draw.getTraceParticle().markElementListInserted(a), this.draw.spliceElementList(i, o, 0, a), this.draw.render({ isSetCursor: !1 });
	}
	deleteArea(e = {}) {
		let t = e.id || this.getActiveAreaId();
		if (!t) return;
		let n = this.areaInfoMap.get(t);
		if (!n) return;
		let { positionList: r } = n, i = n.sourceElementList;
		this.draw.deleteElementList(i, r[0].index, r.length, { isIgnoreDeletedRule: !0 }), this.draw.render({ isSetCursor: !1 });
	}
}, no = class {
	draw;
	options;
	imageCache;
	mainBadge;
	areaBadgeMap;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.imageCache = /* @__PURE__ */ new Map(), this.mainBadge = null, this.areaBadgeMap = /* @__PURE__ */ new Map();
	}
	setMainBadge(e) {
		this.mainBadge = e;
	}
	setAreaBadgeMap(e) {
		this.areaBadgeMap.clear(), e.forEach((e) => {
			this.areaBadgeMap.set(e.areaId, e.badge);
		});
	}
	_drawImage(e, t, n, r, i, a) {
		if (this.imageCache.has(a)) {
			let o = this.imageCache.get(a);
			e.drawImage(o, t, n, r, i);
		} else {
			let o = new Image();
			o.setAttribute("crossOrigin", "Anonymous"), o.src = a, o.onload = () => {
				this.imageCache.set(a, o), e.drawImage(o, t, n, r, i);
			};
		}
	}
	render(e, t) {
		if (t === 0 && this.mainBadge) {
			let { scale: t, badge: n } = this.options, { left: r, top: i, width: a, height: o, value: s } = this.mainBadge, c = this.draw.getMargins()[0] + this.draw.getHeader().getExtraHeight(), l = (r || n.left) * t, u = (i || n.top) * t + c;
			this._drawImage(e, l, u, a * t, o * t, s);
		}
		if (this.areaBadgeMap.size) {
			let n = this.draw.getArea().getAreaInfo();
			if (n.size) {
				let { scale: r, badge: i } = this.options;
				for (let a of n) {
					let { positionList: n } = a[1], o = n[0];
					if (o.pageNo !== t) continue;
					let s = this.areaBadgeMap.get(a[0]);
					if (!s) continue;
					let { left: c, top: l, width: u, height: d, value: f } = s, p = (c || i.left) * r, m = (l || i.top) * r + o.coordinate.leftTop[1];
					this._drawImage(e, p, m, u * r, d * r, f);
				}
			}
		}
	}
}, ro = class {
	draw;
	options;
	data;
	pageContainer;
	isDrawing = !1;
	startStroke = null;
	constructor(e, t) {
		this.draw = e, this.options = e.getOptions(), this.data = t || [], this.pageContainer = e.getPageContainer(), this.register();
	}
	register() {
		this.pageContainer.addEventListener("mousedown", this.start.bind(this)), this.pageContainer.addEventListener("mouseup", this.stop.bind(this)), this.pageContainer.addEventListener("mouseleave", this.stop.bind(this)), this.pageContainer.addEventListener("mousemove", this.drawing.bind(this));
	}
	start(e) {
		if (!this.draw.isGraffitiMode()) return;
		this.isDrawing = !0;
		let { scale: t } = this.options;
		this.startStroke = {
			lineColor: this.options.graffiti.defaultLineColor,
			lineWidth: this.options.graffiti.defaultLineWidth,
			points: [e.offsetX / t, e.offsetY / t]
		};
	}
	stop() {
		this.isDrawing = !1;
	}
	drawing(e) {
		if (!this.isDrawing || !this.draw.isGraffitiMode()) return;
		let { offsetX: t, offsetY: n } = e;
		if (this.startStroke && Math.abs(this.startStroke.points[0] - t) < 2 && Math.abs(this.startStroke.points[1] - n) < 2) return;
		let r = this.draw.getPageNo(), i = this.data.find((e) => e.pageNo === r);
		if (this.startStroke &&= (i || (i = {
			pageNo: r,
			strokes: []
		}, this.data.push(i)), i.strokes.push(this.startStroke), null), !i?.strokes?.length) return;
		let { scale: a } = this.options;
		i.strokes[i.strokes.length - 1].points.push(t / a, n / a), this.draw.render({
			isCompute: !1,
			isSetCursor: !1,
			isSubmitHistory: !1
		});
	}
	getValue() {
		return this.data;
	}
	compute() {
		let e = this.draw.getPageRowList().length;
		for (let t = this.data.length - 1; t >= 0; t--) this.data[t].pageNo > e - 1 && this.data.splice(t, 1);
	}
	clear() {
		this.data = [];
	}
	render(e, t) {
		let n = this.data.find((e) => e.pageNo === t)?.strokes;
		if (!n?.length) return;
		let { graffiti: { defaultLineColor: r, defaultLineWidth: i }, scale: a } = this.options;
		e.save();
		for (let t = 0; t < n.length; t++) {
			let o = n[t];
			e.beginPath(), e.strokeStyle = o.lineColor || r, e.lineWidth = (o.lineWidth || i) * a, e.moveTo(o.points[0] * a, o.points[1] * a);
			for (let t = 2; t < o.points.length; t += 2) e.lineTo(o.points[t] * a, o.points[t + 1] * a);
			e.stroke();
		}
		e.restore();
	}
}, io = class {
	draw;
	options;
	canvas;
	isActive;
	container;
	constructor(e) {
		this.draw = e, this.options = e.getOptions(), this.container = e.getContainer(), this.isActive = !1;
		let t = this._createMagnifierCanvas();
		this.container.appendChild(t), this.canvas = t, this._addEvent();
	}
	_createMagnifierCanvas() {
		let { magnifier: e } = this.options, t = document.createElement("canvas");
		return t.classList.add("ce-magnifier"), t.width = e.size, t.height = e.size, t.style.width = `${e.size}px`, t.style.height = `${e.size}px`, t;
	}
	_addEvent() {
		this.container.addEventListener("mousemove", this._mousemove), document.addEventListener("keydown", this._handleKeyDown), document.addEventListener("keyup", this._handleKeyUp);
	}
	_removeEvent() {
		this.container.removeEventListener("mousemove", this._mousemove), document.removeEventListener("keydown", this._handleKeyDown), document.removeEventListener("keyup", this._handleKeyUp);
	}
	_handleKeyDown = (e) => {
		e.key === Z.ALT && this.show();
	};
	_handleKeyUp = (e) => {
		e.key === Z.ALT && this.hide();
	};
	_mousemove = (e) => {
		this.isActive && this._update(e);
	};
	show() {
		this.options.magnifier.disabled || (this.isActive = !0, this.canvas.style.display = "block");
	}
	hide() {
		this.options.magnifier.disabled || (this.isActive = !1, this.canvas.style.display = "none");
	}
	_update(e) {
		if (!this.isActive) return;
		let t = this.canvas.getContext("2d"), { magnifier: { size: n, zoom: r, borderColor: i } } = this.options, a = n / 2, o = n / r;
		this.canvas.style.left = `${e.clientX - a}px`, this.canvas.style.top = `${e.clientY - a}px`;
		let s = this.draw.getPageList(), c = null, l = 0, u = 0;
		for (let t = 0; t < s.length; t++) {
			let n = s[t], r = n.getBoundingClientRect();
			if (e.clientX >= r.left && e.clientX <= r.right && e.clientY >= r.top && e.clientY <= r.bottom) {
				c = n;
				let t = c.width / r.width;
				l = (e.clientX - r.left) * t - o / 2, u = (e.clientY - r.top) * t - o / 2;
				break;
			}
		}
		t.clearRect(0, 0, n, n), c && (t.save(), t.beginPath(), t.arc(a, a, a - 1, 0, Math.PI * 2), t.closePath(), t.clip(), t.drawImage(c, Math.max(0, l), Math.max(0, u), o, o, 0, 0, n, n), t.restore(), t.beginPath(), t.arc(a, a, a - 1, 0, Math.PI * 2), t.strokeStyle = i, t.lineWidth = 2, t.stroke());
	}
	destroy() {
		this.canvas.remove(), this._removeEvent();
	}
}, ao = class {
	draw;
	i18n;
	disabled;
	assertiveDom = null;
	rangeChangeHandler = null;
	constructor(e) {
		if (this.draw = e, this.i18n = e.getI18n(), this.disabled = e.getOptions().accessibility.disabled, this.disabled) return;
		let t = document.createElement("div");
		t.className = "ce-sr-only", this.assertiveDom = document.createElement("div"), this.assertiveDom.setAttribute("aria-live", "assertive"), this.assertiveDom.setAttribute("aria-atomic", "true"), t.appendChild(this.assertiveDom), e.getContainer().appendChild(t), this.rangeChangeHandler = this.handleRangeChange.bind(this), this.draw.getEventBus().on("rangeChange", this.rangeChangeHandler);
	}
	handleRangeChange(e) {
		e.startIndex !== e.endIndex && this.selection();
	}
	selection() {
		if (this.disabled) return;
		let e = this.draw.getRange().toString();
		if (!e.trim()) return;
		let t = this.i18n.t("accessibility.selected");
		this.assertive(`${t}${e}`);
	}
	input(e) {
		if (this.disabled) return;
		let t = e.replace(/* @__PURE__ */ RegExp("​", "g"), "").replace(/\n/g, "");
		if (!t.trim()) return;
		let n = this.i18n.t("accessibility.input");
		this.assertive(`${n}${t}`);
	}
	assertive(e) {
		this.disabled || !this.assertiveDom || (this.assertiveDom.textContent = "", this.assertiveDom.offsetHeight, this.assertiveDom.textContent = e);
	}
	destroy() {
		this.disabled || (this.rangeChangeHandler && this.draw.getEventBus().off("rangeChange", this.rangeChangeHandler), this.assertiveDom?.parentElement?.remove());
	}
}, oo = class {
	container;
	pageContainer;
	pageList;
	ctxList;
	pageNo;
	renderCount;
	pagePixelRatio;
	mode;
	options;
	position;
	zone;
	elementList;
	listener;
	eventBus;
	override;
	i18n;
	canvasEvent;
	globalEvent;
	cursor;
	range;
	margin;
	background;
	badge;
	magnifier;
	search;
	spellcheck;
	group;
	area;
	underline;
	strikeout;
	highlight;
	historyManager;
	previewer;
	imageParticle;
	laTexParticle;
	textParticle;
	tableParticle;
	tablePaging;
	tableTool;
	tableOperate;
	pageNumber;
	lineNumber;
	waterMark;
	placeholder;
	header;
	footer;
	hyperlinkParticle;
	hintParticle;
	traceParticle;
	labelParticle;
	dateParticle;
	separatorParticle;
	pageBreakParticle;
	superscriptParticle;
	subscriptParticle;
	checkboxParticle;
	radioParticle;
	blockParticle;
	listParticle;
	lineBreakParticle;
	whiteSpaceParticle;
	control;
	cascadeManager;
	validate;
	pageBorder;
	workerManager;
	scrollObserver;
	selectionObserver;
	imageObserver;
	graffiti;
	accessibility;
	LETTER_REG;
	WORD_LIKE_REG;
	rowList;
	pageRowList;
	pageDirectionList;
	painterStyle;
	painterOptions;
	visiblePageNoList;
	intersectionPageNo;
	lazyRenderIntersectionObserver;
	printModeData;
	controlMinWidthPlaceholderElementListSet;
	columnManager;
	ruler;
	constructor(e, t, n, r, i, a) {
		this.container = this._wrapContainer(e), this.pageList = [], this.ctxList = [], this.pageNo = 0, this.renderCount = 0, this.pagePixelRatio = null, this.mode = t.mode, this.options = t, this.elementList = n.main, this.pageDirectionList = [t.paperDirection], this.listener = r, this.eventBus = i, this.override = a, this._formatContainer(), this.pageContainer = this._createPageContainer(), this._createPage(0), this.i18n = new Ra(t.locale), this.historyManager = new Qr(this), this.position = new $r(this), this.zone = new Va(this), this.range = new ei(this), this.margin = new ii(this), this.background = new ti(this), this.badge = new no(this), this.magnifier = new io(this), this.search = new ai(this), this.spellcheck = new oi(this), this.group = new Ka(this), this.area = new to(this), this.underline = new ui(this), this.strikeout = new si(this), this.highlight = new ri(this), this.previewer = new ja(this), this.imageParticle = new Ke(this), this.laTexParticle = new pt(this), this.textParticle = new di(this), this.tableParticle = new hi(this), this.tablePaging = new gi(this), this.tableTool = new vi(this), this.tableOperate = new $a(this), this.pageNumber = new fi(this), this.lineNumber = new Ya(this), this.waterMark = new Ai(this), this.placeholder = new Ga(this), this.header = new Ti(this, n.header), this.footer = new Ha(this, n.footer), this.hyperlinkParticle = new xi(this), this.hintParticle = new Si(this), this.traceParticle = new Ci(this), this.labelParticle = new wi(this), this.dateParticle = new Ma(this), this.separatorParticle = new Oi(this), this.pageBreakParticle = new ki(this), this.superscriptParticle = new Ei(), this.subscriptParticle = new Di(), this.checkboxParticle = new pa(this), this.radioParticle = new ma(this), this.blockParticle = new Fa(this), this.listParticle = new Ua(this), this.lineBreakParticle = new Wa(this), this.whiteSpaceParticle = new qa(this), this.control = new zi(this), this.cascadeManager = new da(this), this.validate = new fa(this), this.pageBorder = new Xa(this), this.graffiti = new ro(this, n.graffiti), this.columnManager = new y(this), this.ruler = new bi(this), this.scrollObserver = new pi(this), this.selectionObserver = new mi(this), this.imageObserver = new za(), new Ja(this), this.canvasEvent = new Yr(this), this.cursor = new ir(this, this.canvasEvent), this.canvasEvent.register(), this.globalEvent = new Zr(this, this.canvasEvent), this.globalEvent.register(), this.workerManager = new Aa(this), new Qa(this), this.accessibility = new ao(this);
		let { letterClass: o } = t;
		this.LETTER_REG = RegExp(`[${o.join("")}]`), this.WORD_LIKE_REG = RegExp(`${o.map((e) => `[^${e}][${e}]`).join("|")}`), this.rowList = [], this.pageRowList = [], this.painterStyle = null, this.painterOptions = null, this.visiblePageNoList = [], this.intersectionPageNo = 0, this.lazyRenderIntersectionObserver = null, this.printModeData = null, this.controlMinWidthPlaceholderElementListSet = /* @__PURE__ */ new WeakSet(), this.mode === p.PRINT && this.setPrintData(), this.render({
			isInit: !0,
			isSetCursor: !1,
			isFirstRender: !0
		}), this.cascadeManager.executeAll();
	}
	setPrintData() {
		this.printModeData = {
			header: this.header.getElementList(),
			main: this.elementList,
			footer: this.footer.getElementList()
		};
		let e = k(this.printModeData);
		[
			"header",
			"main",
			"footer"
		].forEach((t) => {
			e[t] = this.control.filterAssistElement(e[t]);
		}), this.setEditorData(e);
	}
	clearPrintData() {
		this.printModeData &&= (this.setEditorData(this.printModeData), null);
	}
	getLetterReg() {
		return this.LETTER_REG;
	}
	getMode() {
		return this.mode;
	}
	setMode(e) {
		this.mode !== e && (e === p.PRINT && this.setPrintData(), this.mode === p.PRINT && this.clearPrintData(), this.clearSideEffect(), this.range.clearRange(), this.mode = e, this.options.mode = e, this.render({
			isSetCursor: !1,
			isSubmitHistory: !1
		}));
	}
	isReadonly() {
		if (this.area.getActiveAreaInfo()?.area?.mode) return this.area.isReadonly();
		switch (this.mode) {
			case p.DESIGN: return !1;
			case p.READONLY:
			case p.PRINT:
			case p.GRAFFITI:
			case p.TRACE: return !0;
			case p.FORM: return !this.control.getIsRangeWithinControl();
			default: return !1;
		}
	}
	isDisabled() {
		if (this.mode === p.DESIGN) return !1;
		let { startIndex: e, endIndex: t } = this.range.getRange(), n = this.getElementList();
		if (this.getTd()?.disabled) return !0;
		if (e === t) {
			let t = n[e], r = n[e + 1];
			return !!(t?.title?.disabled && r?.title?.disabled && t.titleId === r.titleId || t?.control?.disabled && r?.control?.disabled && t.controlId === r.controlId);
		}
		return n.slice(e + 1, t + 1).some((e) => e.title?.disabled || e.control?.disabled);
	}
	isDesignMode() {
		return this.mode === p.DESIGN;
	}
	isPrintMode() {
		return this.mode === p.PRINT;
	}
	isAreaHideDisabled() {
		return this.isDesignMode() || this.isPrintMode() && this.options.modeRule[p.PRINT].areaHideDisabled;
	}
	isGraffitiMode() {
		return this.mode === p.GRAFFITI;
	}
	isTraceMode() {
		return this.mode === p.TRACE;
	}
	setTraceEnabled(e) {
		this.mode !== p.TRACE && !this.options.trace.disabled !== e && (this.options.trace.disabled = !e, this.render({
			isSetCursor: !1,
			isSubmitHistory: !1
		}));
	}
	setRulerEnabled(e) {
		!this.options.ruler.disabled !== e && this.ruler.setEnabled(e);
	}
	deleteElementList(e, t, n = 1, r) {
		return this.options.trace.disabled ? (this.spliceElementList(e, t, n, void 0, { isIgnoreDeletedRule: r?.isIgnoreDeletedRule }), []) : this.traceParticle.markElementListDeleted(e.slice(t, t + n), r);
	}
	getOriginalWidth(e = this.options.paperDirection) {
		let { width: t, height: n } = this.options;
		return e === g.VERTICAL ? t : n;
	}
	getOriginalHeight(e = this.options.paperDirection) {
		let { width: t, height: n } = this.options;
		return e === g.VERTICAL ? n : t;
	}
	getWidth(e = this.options.paperDirection) {
		return Math.floor(this.getOriginalWidth(e) * this.options.scale);
	}
	getHeight(e = this.options.paperDirection) {
		return Math.floor(this.getOriginalHeight(e) * this.options.scale);
	}
	getMainHeight() {
		return this.getHeight() - this.getMainOuterHeight();
	}
	getMainOuterHeight(e, t) {
		let n = t || (e === void 0 ? this.options.paperDirection : this.getPageDirection(e)), r = this.getMargins(n), i = this.header.getExtraHeight(e, n), a = this.footer.getExtraHeight(e, n);
		return r[0] + r[2] + i + a;
	}
	getCanvasWidth(e = -1) {
		return this.getPage(e).width;
	}
	getCanvasHeight(e = -1) {
		return this.getPage(e).height;
	}
	getInnerWidth(e = this.options.paperDirection) {
		let t = this.getWidth(e), n = this.getMargins(e);
		return t - n[1] - n[3];
	}
	getColumnLayout(e) {
		return this.columnManager.getLayout(e);
	}
	setColumnConfig(e) {
		this.options.pageMode !== h.CONTINUITY && this.columnManager.setConfig(e);
	}
	getOriginalInnerWidth() {
		let e = this.getOriginalWidth(), t = this.getOriginalMargins();
		return e - t[1] - t[3];
	}
	getContextInnerWidth() {
		let e = this.position.getPositionContext();
		if (e.isTable) {
			let t = this.getOriginalElementList(), n = this.position.getTableTdByContext(t, e), r = this.getTdPadding();
			return n.width - r[1] - r[3];
		}
		let t = this.getColumnLayout();
		return t && t.count > 1 ? t.width / this.options.scale : this.getOriginalInnerWidth();
	}
	getMargins(e = this.options.paperDirection) {
		return this.getOriginalMargins(e).map((e) => e * this.options.scale);
	}
	getOriginalMargins(e = this.options.paperDirection) {
		let { margins: t } = this.options;
		return e === g.VERTICAL ? t : [
			t[1],
			t[2],
			t[3],
			t[0]
		];
	}
	getPageDirection(e) {
		return this.pageDirectionList[e] || this.options.paperDirection;
	}
	getPageDirectionList() {
		return this.pageDirectionList;
	}
	getPageSize(e) {
		let t = this.getPageDirection(e), n = this.getMargins(t), r = this.getWidth(t);
		return {
			width: r,
			height: this.getHeight(t),
			margins: n,
			innerWidth: r - n[1] - n[3]
		};
	}
	getPageOffset(e, t = !1) {
		let n = (e) => t ? this.getOriginalWidth(e) : this.getWidth(e), r = (e) => t ? this.getOriginalHeight(e) : this.getHeight(e), i = t ? this.options.pageGap : this.getPageGap(), a = 0;
		for (let t = 0; t < e; t++) a += r(this.getPageDirection(t)) + i;
		let o = n(this.getPageDirection(e));
		return {
			x: (this._getPageMaxWidth(t) - o) / 2,
			y: a
		};
	}
	_getPageMaxWidth(e = !1) {
		let t = e ? this.getOriginalWidth() : this.getWidth();
		if (!this.pageDirectionList.some((e) => e !== this.options.paperDirection)) return t;
		let n = e ? this.getOriginalHeight() : this.getHeight();
		return Math.max(t, n);
	}
	getPageGap() {
		return this.options.pageGap * this.options.scale;
	}
	getOriginalPageGap() {
		return this.options.pageGap;
	}
	getPageNumberBottom() {
		let { pageNumber: { bottom: e }, scale: t } = this.options;
		return e * t;
	}
	getMarginIndicatorSize() {
		return this.options.marginIndicatorSize * this.options.scale;
	}
	getDefaultBasicRowMarginHeight() {
		return this.options.defaultBasicRowMarginHeight * this.options.scale;
	}
	getHighlightMarginHeight() {
		return this.options.highlightMarginHeight * this.options.scale;
	}
	getTdPadding() {
		let { table: { tdPadding: e }, scale: t } = this.options;
		return e.map((e) => e * t);
	}
	getContainer() {
		return this.container;
	}
	getPageContainer() {
		return this.pageContainer;
	}
	getVisiblePageNoList() {
		return this.visiblePageNoList;
	}
	setVisiblePageNoList(e) {
		this.visiblePageNoList = e, this.listener.visiblePageNoListChange && this.listener.visiblePageNoListChange(this.visiblePageNoList), this.eventBus.isSubscribe("visiblePageNoListChange") && this.eventBus.emit("visiblePageNoListChange", this.visiblePageNoList);
	}
	getIntersectionPageNo() {
		return this.intersectionPageNo;
	}
	setIntersectionPageNo(e) {
		this.intersectionPageNo = e, this.listener.intersectionPageNoChange && this.listener.intersectionPageNoChange(this.intersectionPageNo), this.eventBus.isSubscribe("intersectionPageNoChange") && this.eventBus.emit("intersectionPageNoChange", this.intersectionPageNo);
	}
	getPageNo() {
		return this.pageNo;
	}
	setPageNo(e) {
		this.pageNo = e;
	}
	getRenderCount() {
		return this.renderCount;
	}
	getPage(e = -1) {
		return this.pageList[~e ? e : this.pageNo];
	}
	getPageList() {
		return this.pageList;
	}
	getPageCount() {
		return this.pageList.length;
	}
	getTableRowList(e) {
		let t = this.position.getPositionContext();
		return this.position.getTableTdByContext(e, t).rowList;
	}
	getOriginalRowList() {
		let e = this.getZone();
		return e.isHeaderActive() ? this.header.getRowList() : e.isFooterActive() ? this.footer.getRowList() : this.rowList;
	}
	getRowList() {
		return this.position.getPositionContext().isTable ? this.getTableRowList(this.getOriginalElementList()) : this.getOriginalRowList();
	}
	getPageRowList() {
		return this.pageRowList;
	}
	getCtx() {
		return this.ctxList[this.pageNo];
	}
	getOptions() {
		return this.options;
	}
	getSearch() {
		return this.search;
	}
	getSpellcheck() {
		return this.spellcheck;
	}
	getGroup() {
		return this.group;
	}
	getArea() {
		return this.area;
	}
	getBadge() {
		return this.badge;
	}
	getMagnifier() {
		return this.magnifier;
	}
	getHistoryManager() {
		return this.historyManager;
	}
	getPosition() {
		return this.position;
	}
	getZone() {
		return this.zone;
	}
	getColumnManager() {
		return this.columnManager;
	}
	getRange() {
		return this.range;
	}
	getLineBreakParticle() {
		return this.lineBreakParticle;
	}
	getTextParticle() {
		return this.textParticle;
	}
	getStrikeout() {
		return this.strikeout;
	}
	getUnderline() {
		return this.underline;
	}
	getSubscriptParticle() {
		return this.subscriptParticle;
	}
	getSuperscriptParticle() {
		return this.superscriptParticle;
	}
	getHeaderElementList() {
		return this.header.getElementList();
	}
	getTableElementList(e) {
		let t = this.position.getPositionContext();
		return this.position.getTableTdByContext(e, t)?.value || [];
	}
	getElementList() {
		let e = this.position.getPositionContext(), t = this.getOriginalElementList();
		return e.isTable ? this.getTableElementList(t) : t;
	}
	getMainElementList() {
		return this.position.getPositionContext().isTable ? this.getTableElementList(this.elementList) : this.elementList;
	}
	getOriginalElementList() {
		let e = this.getZone();
		return e.isHeaderActive() ? this.getHeaderElementList() : e.isFooterActive() ? this.getFooterElementList() : this.elementList;
	}
	getOriginalMainElementList() {
		return this.elementList;
	}
	getFooterElementList() {
		return this.footer.getElementList();
	}
	getTd() {
		let e = this.position.getPositionContext();
		return e.isTable ? this.position.getTableTdByContext(this.getOriginalElementList(), e) : null;
	}
	insertElementList(e, t = {}) {
		if (!e.length || !this.range.getIsCanInput()) return;
		let { startIndex: n, endIndex: r } = this.range.getRange();
		if (!~n && !~r) return;
		let { isSubmitHistory: i = !0 } = t;
		yn(e, {
			isHandleFirstElement: !1,
			editorOptions: this.options
		}), this.traceParticle.markElementListInserted(e);
		let a = -1, o = this.control.getActiveControl();
		if (!o && this.control.getIsRangeWithinControl() && (this.control.initControl(), o = this.control.getActiveControl()), o && this.control.getIsRangeWithinControl()) a = o.setValue(e, void 0, { isIgnoreDisabledRule: !0 }), this.control.emitControlContentChange();
		else {
			let t = this.getElementList(), i = n === r, o = n + 1;
			i || this.deleteElementList(t, o, r - n), this.spliceElementList(t, o, 0, e), a = n + e.length;
			let s = t[o - 1];
			e[0].listId && s && !s.listId && s?.value === "​" && (!s.type || s.type === H.TEXT) && (t.splice(n, 1), --a);
		}
		~a && (this.range.setRange(a, a), this.render({
			curIndex: a,
			isSubmitHistory: i
		}));
	}
	appendElementList(e, t = {}) {
		if (!e.length) return;
		yn(e, {
			isHandleFirstElement: !1,
			editorOptions: this.options
		}), this.traceParticle.markElementListInserted(e);
		let n, { isPrepend: r, isSubmitHistory: i = !0 } = t;
		r ? (this.elementList.splice(1, 0, ...e), n = e.length) : (this.elementList.push(...e), n = this.elementList.length - 1), this.range.setRange(n, n), this.render({
			curIndex: n,
			isSubmitHistory: i
		});
	}
	spliceElementList(e, t, n, r, i) {
		let { isIgnoreDeletedRule: a = !1 } = i || {}, { group: o, modeRule: s } = this.options;
		if (n > 0) {
			let r = t + n, i = e[r]?.listId;
			if (i && e[t - 1]?.listId !== i) {
				let t = r;
				for (; t < e.length;) {
					let n = e[t];
					if (n.listId !== i || n.value === "​") break;
					delete n.listId, delete n.listType, delete n.listStyle, t++;
				}
			}
			if (!a && !this.isDesignMode() && !this.control.getIsRangeWithinControl()) {
				let n = this.getTd()?.deletable, i = r - 1;
				for (; i >= t;) {
					let t = e[i];
					if (t?.trace?.length && t.trace[t.trace.length - 1].type === J.DELETED) {
						i--;
						continue;
					}
					(t?.hide || t?.control?.hide || t?.area?.hide || n !== !1 && t?.control?.deletable !== !1 && (!t.controlId || this.mode !== p.FORM || !s[this.mode].controlDeletableDisabled) && t?.title?.deletable !== !1 && (o.deletable !== !1 || !t.groupIds?.length) && (t?.area?.deletable !== !1 || t?.areaIndex !== 0)) && e.splice(i, 1), i--;
				}
			} else {
				let n = r - 1;
				for (; n >= t;) {
					let t = e[n];
					(!t?.trace?.length || t.trace[t.trace.length - 1].type !== J.DELETED) && e.splice(n, 1), n--;
				}
			}
		}
		if (r?.length) for (let n = 0; n < r.length; n++) e.splice(t + n, 0, r[n]);
	}
	getCanvasEvent() {
		return this.canvasEvent;
	}
	getGlobalEvent() {
		return this.globalEvent;
	}
	getListener() {
		return this.listener;
	}
	getEventBus() {
		return this.eventBus;
	}
	getOverride() {
		return this.override;
	}
	getCursor() {
		return this.cursor;
	}
	getPreviewer() {
		return this.previewer;
	}
	getImageParticle() {
		return this.imageParticle;
	}
	getTableTool() {
		return this.tableTool;
	}
	getRuler() {
		return this.ruler;
	}
	getTableOperate() {
		return this.tableOperate;
	}
	getTableParticle() {
		return this.tableParticle;
	}
	getBlockParticle() {
		return this.blockParticle;
	}
	getHeader() {
		return this.header;
	}
	getFooter() {
		return this.footer;
	}
	getHyperlinkParticle() {
		return this.hyperlinkParticle;
	}
	getHintParticle() {
		return this.hintParticle;
	}
	getTraceParticle() {
		return this.traceParticle;
	}
	getDateParticle() {
		return this.dateParticle;
	}
	getListParticle() {
		return this.listParticle;
	}
	getCheckboxParticle() {
		return this.checkboxParticle;
	}
	getRadioParticle() {
		return this.radioParticle;
	}
	getControl() {
		return this.control;
	}
	getCascadeManager() {
		return this.cascadeManager;
	}
	getValidate() {
		return this.validate;
	}
	getWorkerManager() {
		return this.workerManager;
	}
	getImageObserver() {
		return this.imageObserver;
	}
	getI18n() {
		return this.i18n;
	}
	getGraffiti() {
		return this.graffiti;
	}
	getAccessibility() {
		return this.accessibility;
	}
	getRowCount() {
		return this.getRowList().length;
	}
	async getDataURL(e = {}) {
		let { pixelRatio: t, mode: n, snapDomFunction: r } = e;
		t && this.setPagePixelRatio(t);
		let i = this.mode, a = !!n && i !== n;
		a && this.setMode(n), this.render({
			isLazy: !1,
			isCompute: !1,
			isSetCursor: !1,
			isSubmitHistory: !1
		}), await this.imageObserver.allSettled(), r && await this.blockParticle.drawIframeToPage(this.pageList, r);
		let o = this.pageList.map((e) => e.toDataURL());
		return t && this.setPagePixelRatio(null), a && this.setMode(i), o;
	}
	getPainterStyle() {
		return this.painterStyle && Object.keys(this.painterStyle).length ? this.painterStyle : null;
	}
	getPainterOptions() {
		return this.painterOptions;
	}
	setPainterStyle(e, t) {
		this.painterStyle = e, this.painterOptions = t || null, this.getPainterStyle() && this.pageList.forEach((e) => e.style.cursor = "copy");
	}
	setDefaultRange() {
		this.elementList.length && setTimeout(() => {
			let e = this.elementList.length - 1;
			this.range.setRange(e, e), this.range.setRangeStyle();
		});
	}
	getIsPagingMode() {
		return this.options.pageMode === h.PAGING;
	}
	setPageMode(e) {
		if (!e || this.options.pageMode === e) return;
		if (this.options.pageMode = e, e === h.PAGING) {
			let { height: e } = this.options, t = this.getPagePixelRatio(), n = this.pageList[0];
			n.style.height = `${e}px`, n.height = e * t, this._initPageContext(this.ctxList[0]);
		} else this._disconnectLazyRender(), this.header.recovery(), this.footer.recovery(), this.zone.setZone(m.MAIN);
		let { startIndex: t } = this.range.getRange(), n = this.range.getIsCollapsed();
		this.render({
			isSetCursor: !0,
			curIndex: t,
			isSubmitHistory: !1
		}), n || this.cursor.drawCursor({ isShow: !1 }), setTimeout(() => {
			this.listener.pageModeChange && this.listener.pageModeChange(e), this.eventBus.isSubscribe("pageModeChange") && this.eventBus.emit("pageModeChange", e);
		});
	}
	setPageScale(e) {
		this.options.scale = e, this._updatePageSizes();
		let t = this.position.getCursorPosition();
		this.render({
			isSubmitHistory: !1,
			isSetCursor: !!t,
			curIndex: t?.index
		}), this.listener.pageScaleChange && this.listener.pageScaleChange(e), this.eventBus.isSubscribe("pageScaleChange") && this.eventBus.emit("pageScaleChange", e);
	}
	getPagePixelRatio() {
		return this.pagePixelRatio || window.devicePixelRatio;
	}
	setPagePixelRatio(e) {
		!this.pagePixelRatio && e === window.devicePixelRatio || e === this.pagePixelRatio || (this.pagePixelRatio = e, this.setPageDevicePixel());
	}
	setPageDevicePixel() {
		this._updatePageSizes(), this.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		});
	}
	setPaperSize(e, t) {
		this.options.width = e, this.options.height = t, this._updatePageSizes(), this.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		});
	}
	setPaperDirection(e) {
		this.options.paperDirection = e, this.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		});
	}
	setPageDirection(e) {
		if (this.isReadonly() || this.isDisabled() || this.zone.getZone() !== m.MAIN) return;
		let { endIndex: t } = this.range.getRange(), n = null;
		for (let e = t; e >= 0; e--) if (this.elementList[e].type === H.PAGE_BREAK) {
			n = this.elementList[e];
			break;
		}
		if (!n) {
			e && this.setPaperDirection(e);
			return;
		}
		e ? n.paperDirection = e : delete n.paperDirection, this.render({ curIndex: t });
	}
	setPaperMargin(e) {
		this.options.margins = e, this.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		});
	}
	getOriginValue(e = {}) {
		let { pageNo: t } = e, n = this.elementList;
		return Number.isInteger(t) && t >= 0 && t < this.pageRowList.length && (n = this.pageRowList[t].flatMap((e) => e.elementList)), this.blockParticle.update(), {
			header: this.getHeaderElementList(),
			main: n,
			footer: this.getFooterElementList(),
			graffiti: this.graffiti.getValue()
		};
	}
	getValue(t = {}) {
		let n = this.getOriginValue(t), { extraPickAttrs: r } = t;
		return {
			version: e,
			data: {
				header: X(n.header, { extraPickAttrs: r }),
				main: X(n.main, {
					extraPickAttrs: r,
					isClassifyArea: !0
				}),
				footer: X(n.footer, { extraPickAttrs: r }),
				graffiti: n.graffiti
			},
			options: k(this.options)
		};
	}
	setValue(e, t) {
		let { header: n, main: r, footer: i } = k(e);
		if (!n && !r && !i) return;
		let { isSetCursor: a = !1 } = t || {};
		[
			n,
			r,
			i
		].forEach((e) => {
			e && yn(e, {
				editorOptions: this.options,
				isForceCompensation: !0
			});
		}), this.setEditorData({
			header: n,
			main: r,
			footer: i
		}), this.historyManager.recovery();
		let o = a ? r?.length ? r.length - 1 : 0 : void 0;
		o !== void 0 && this.range.setRange(o, o), this.render({
			curIndex: o,
			isSetCursor: a,
			isFirstRender: !0
		}), this.cascadeManager.executeAll();
	}
	setEditorData(e) {
		let { header: t, main: n, footer: r } = e;
		t && this.header.setElementList(t), n && (this.elementList = n), r && this.footer.setElementList(r);
	}
	_wrapContainer(e) {
		let t = document.createElement("div");
		return e.append(t), t;
	}
	_formatContainer() {
		this.container.style.position = "relative", this.container.style.width = `${this.getWidth()}px`, this.container.setAttribute(_e, d.MAIN);
	}
	_createPageContainer() {
		let e = document.createElement("div");
		return e.classList.add("ce-page-container"), this.container.append(e), e;
	}
	_createPage(e) {
		let { width: t, height: n } = this.getPageSize(e), r = document.createElement("canvas");
		r.style.width = `${t}px`, r.style.height = `${n}px`, r.style.display = "block", r.style.backgroundColor = "#ffffff", r.style.marginLeft = "auto", r.style.marginRight = "auto", r.style.marginBottom = `${this.getPageGap()}px`, r.setAttribute("data-index", String(e)), this.pageContainer.append(r);
		let i = this.getPagePixelRatio();
		r.width = t * i, r.height = n * i, r.style.cursor = "text";
		let a = r.getContext("2d");
		this._initPageContext(a), this.pageList.push(r), this.ctxList.push(a);
	}
	_updatePageSizes() {
		let e = this.getPagePixelRatio(), t = this.getIsPagingMode();
		this.container.style.width = `${this._getPageMaxWidth()}px`, this.pageList.forEach((n, r) => {
			let { width: i, height: a } = this.getPageSize(r);
			n.style.width = `${i}px`, n.style.marginBottom = `${this.getPageGap()}px`, t && (n.style.height = `${a}px`);
			let o = t ? a : Number.parseFloat(n.style.height) || a, s = Math.floor(i * e), c = Math.floor(o * e);
			(n.width !== s || n.height !== c) && (n.width = s, n.height = c, this._initPageContext(this.ctxList[r]));
		});
	}
	_initPageContext(e) {
		let t = this.getPagePixelRatio();
		e.scale(t, t), e.letterSpacing = "0px", e.wordSpacing = "0px", e.direction = "ltr";
	}
	getElementFont(e, t = 1) {
		let { defaultSize: n, defaultFont: r } = this.options, i = e.font || r, a = e.actualSize || e.size || n;
		return `${e.italic ? "italic " : ""}${e.bold ? "bold " : ""}${a * t}px ${i}`;
	}
	getElementSize(e) {
		return e.actualSize || e.size || this.options.defaultSize;
	}
	getElementRowMargin(e) {
		let { defaultSize: t, defaultBasicRowMarginHeight: n, defaultRowMargin: r, scale: i } = this.options, a = e.size || t, o = 1;
		return a < 12 ? o = a / 12 : a > 30 && (o = 1 + (a - 30) / 30), n * o * (e.rowMargin ?? r) * i;
	}
	computeRowList(e) {
		let { innerWidth: t, elementList: n, isPagingMode: i = !1, isFromTable: o = !1, startX: s = 0, startY: c = 0, pageHeight: l = 0, surroundElementList: d = [] } = e, { defaultSize: f, scale: p, imgCaption: m, table: { tdPadding: h, defaultColMinWidth: g, overflow: v }, defaultTabWidth: y } = this.options, b = this.getDefaultBasicRowMarginHeight(), x = document.createElement("canvas").getContext("2d");
		if (this.controlMinWidthPlaceholderElementListSet.has(n)) {
			for (let e = n.length - 1; e >= 0; e--) n[e].isControlMinWidthPlaceholder && n.splice(e, 1);
			this.controlMinWidthPlaceholderElementListSet.delete(n);
		}
		let S = this.listParticle.computeListStyle(x, n), C = [], w = i && !o ? this.columnManager.getLayout() : null, T = !!w && w.count > 1;
		n.length && C.push({
			width: 0,
			height: 0,
			ascent: 0,
			elementList: [],
			startIndex: 0,
			rowIndex: 0,
			rowFlex: n?.[0]?.rowFlex || n?.[1]?.rowFlex,
			...T ? { columnIndex: 0 } : {}
		});
		let E = s, D = c, O = 0, k = this.options.paperDirection, A = this.getMargins(k), j = t, M = s, N = l, ee = c;
		i && !o && (ee = A[0] + this.getHeader().getExtraHeight(0), D = ee);
		let P = /* @__PURE__ */ new Map(), F = 0, I = 0;
		for (let e = 0; e < n.length; e++) {
			let t = C[C.length - 1], s = n[e], c = this.getElementRowMargin(s), l = {
				width: 0,
				height: 0,
				boundingBoxAscent: 0,
				boundingBoxDescent: 0
			}, te = t.offsetX || s.listId && (S.get(s.listId) || 0) + (s.listLevel ? this.listParticle.LIST_INDENT_WIDTH * s.listLevel * p : 0) || 0, L = (T && w ? w.width : j) - te, ne = t.elementList.length === 1;
			if (E += ne ? te : 0, D += ne && t.offsetY || 0, (s.hide || s.control?.hide || s.area?.hide && !this.isAreaHideDisabled() || this.traceParticle.isTraceHidden(s)) && !this.isDesignMode()) {
				let e = t.elementList[t.elementList.length - 1];
				l.height = e?.metrics.height || this.options.defaultSize * p, l.boundingBoxAscent = e?.metrics.boundingBoxAscent || 0, l.boundingBoxDescent = e?.metrics.boundingBoxDescent || 0;
			} else if (s.type === H.IMAGE || s.type === H.LATEX) {
				if (s.imgDisplay === r.SURROUND || s.imgDisplay === r.FLOAT_TOP || s.imgDisplay === r.FLOAT_BOTTOM) l.width = 0, l.height = 0, l.boundingBoxDescent = 0;
				else {
					let e = s.width * p, t = s.height * p;
					if (e > L) {
						let n = t * L / e;
						s.width = L / p, s.height = n / p, l.width = L, l.height = n, l.boundingBoxDescent = n;
					} else l.width = e, l.height = t, l.boundingBoxDescent = t;
					if (s.imgCaption?.value) {
						let e = ((s.imgCaption.size || m.size) + (s.imgCaption.top ?? m.top)) * p;
						l.boundingBoxAscent += e;
					}
				}
			} else if (s.type === H.TABLE) {
				let t = h[1] + h[3], r = h[0] + h[2], a = s.trList, o = r + f + c * 2 / p;
				for (let e = 0; e < a.length; e++) {
					let t = a[e];
					t.height = Math.max(o, t.minHeight || 0), t.minHeight = t.height;
				}
				v || (ga(s.colgroup, this.getOriginalInnerWidth(), g), s.translateX = 0), this.tableParticle.computeRowColInfo(s);
				for (let e = 0; e < a.length; e++) {
					let n = a[e];
					for (let o = 0; o < n.tdList.length; o++) {
						let s = n.tdList[o], c = this.computeRowList({
							innerWidth: (s.width - t) * p,
							elementList: s.value,
							isFromTable: !0,
							isPagingMode: i
						}), l = c.reduce((e, t) => e + t.height, 0);
						s.rowList = c;
						let u = l / p + r;
						if (s.height < u) {
							let t = u - s.height, n = a[e + s.rowspan - 1];
							n.height += t, n.tdList.forEach((e) => {
								e.height += t, e.realHeight ? e.realHeight += t : e.realHeight = e.height;
							});
						}
						let d = 0, f = 0, m = 0;
						for (; m < s.rowspan;) {
							let t = a[m + e] || a[e];
							d += t.minHeight, f += t.height, m++;
						}
						s.realMinHeight = d, s.realHeight = f, s.mainHeight = u;
					}
				}
				let u = this.tableParticle.getTrListGroupByCol(a);
				for (let e = 0; e < u.length; e++) {
					let t = u[e], n = -1;
					for (let e = 0; e < t.tdList.length; e++) {
						let r = t.tdList[e], i = r.realHeight, a = r.mainHeight, o = r.realMinHeight, s = a < o ? i - o : i - a;
						(!~n || s < n) && (n = s);
					}
					if (n > 0) {
						let t = a[e];
						t.height -= n, t.tdList.forEach((e) => {
							e.height -= n, e.realHeight -= n;
						});
					}
				}
				this.tableParticle.computeRowColInfo(s);
				let d = this.tableParticle.getTableHeight(s), m = this.tableParticle.getTableWidth(s);
				s.width = m, s.height = d;
				let _ = m * p, y = d * p;
				l.width = _, l.height = y, l.boundingBoxDescent = y, l.boundingBoxAscent = -c, n[e + 1]?.type === H.TABLE && (l.boundingBoxAscent -= c);
			} else if (s.type === H.SEPARATOR) {
				let { separator: { lineWidth: e } } = this.options, t = s.lineWidth || e;
				s.width = L / p, l.width = L, l.height = t * p, l.boundingBoxAscent = -c, l.boundingBoxDescent = -c + l.height;
			} else if (s.type === H.PAGE_BREAK) s.width = L / p, l.width = L, l.height = f;
			else if (s.type === H.RADIO || s.controlComponent === K.RADIO) {
				let { width: e, height: t, gap: n } = this.options.radio, r = e + n * 2;
				s.width = r, l.width = r * p, l.height = t * p;
			} else if (s.type === H.CHECKBOX || s.controlComponent === K.CHECKBOX) {
				let { width: e, height: t, gap: n } = this.options.checkbox, r = e + n * 2;
				s.width = r, l.width = r * p, l.height = t * p;
			} else if (s.type === H.TAB) l.width = y * p, l.height = f * p, l.boundingBoxDescent = 0, l.boundingBoxAscent = this.textParticle.getBasisWordBoundingBoxAscent(x, x.font);
			else if (s.isControlMinWidthPlaceholder) {
				l.width = (s.width || 0) * p, l.height = f * p, x.font = this.getElementFont(s);
				let e = this.textParticle.measureBasisWord(x, s.font);
				l.boundingBoxAscent = e.actualBoundingBoxAscent * p, l.boundingBoxDescent = e.actualBoundingBoxDescent * p;
			} else if (s.type === H.BLOCK) {
				if (!s.width) l.width = L;
				else {
					let e = s.width * p;
					l.width = Math.min(e, L);
				}
				l.height = s.height * p, l.boundingBoxDescent = l.height, l.boundingBoxAscent = 0;
			} else if (s.type === H.LABEL) {
				let { defaultSize: e, label: { defaultPadding: t } } = this.options;
				x.font = this.getElementFont(s);
				let n = this.textParticle.measureText(x, s);
				l.width = (n.width + t[1] + t[3]) * p, l.height = (s.size || e) * p, l.boundingBoxDescent = 0, l.boundingBoxAscent = (t[0] + n.actualBoundingBoxAscent) * p;
			} else {
				let e = s.size || f;
				(s.type === H.SUPERSCRIPT || s.type === H.SUBSCRIPT) && (s.actualSize = Math.ceil(e * .6)), l.height = (s.actualSize || e) * p, x.font = this.getElementFont(s), l.width = this.textParticle.measureText(x, s).width * p, s.letterSpacing && (l.width += s.letterSpacing * p);
				let t = this.textParticle.measureBasisWord(x, s.font);
				l.boundingBoxAscent = t.actualBoundingBoxAscent * p, l.boundingBoxDescent = t.actualBoundingBoxDescent * p, s.type === H.SUPERSCRIPT ? l.boundingBoxAscent += l.height / 2 : s.type === H.SUBSCRIPT && (l.boundingBoxDescent += l.height / 2);
			}
			let re = !s.hide && !this.traceParticle.isTraceHidden(s) && (s.imgDisplay !== r.INLINE && s.type === H.IMAGE || s.type === H.LATEX) ? l.height + c : l.boundingBoxAscent + c, R = c + l.boundingBoxAscent + l.boundingBoxDescent + c, z = Object.assign(s, {
				metrics: l,
				left: 0,
				style: this.getElementFont(s, p)
			});
			if (z.control?.minWidth && !z.isControlMinWidthPlaceholder && !this.traceParticle.isTraceHidden(z) && (z.controlComponent && (F += l.width), z.controlComponent === K.POSTFIX)) {
				let r = z.control.minWidth * p - F, i = Math.max(L - t.width - z.metrics.width, 0);
				this.control.setMinWidthControlInfo({
					row: t,
					rowElement: z,
					availableWidth: L,
					controlRealWidth: F
				});
				let a = r - i, o = [];
				for (; a > 0;) {
					let e = Math.min(a, L);
					o.push({
						...z,
						value: "",
						width: e / p,
						left: 0,
						isControlMinWidthPlaceholder: !0
					}), a -= e;
				}
				o.length && (n.splice(e + 1, 0, ...o), this.controlMinWidthPlaceholderElementListSet.add(n)), F = 0;
			}
			let B = n[e - 1], ie = n[e + 1], V = t.width + l.width;
			if (this.options.wordBreak === _.BREAK_WORD && (!B?.type || B?.type === H.TEXT) && (!s.type || s.type === H.TEXT)) {
				let t = `${B?.value || ""}${s.value}`;
				if (this.WORD_LIKE_REG.test(t)) {
					let { width: t, endElement: r } = this.textParticle.measureWord(x, n, e), i = t * p;
					r && i <= L && (V += i, ie = r);
				}
				let r = this.textParticle.measurePunctuationWidth(x, ie);
				V += r * p;
			}
			s.listId && s.value === "​" && !s.listWrap && (P.has(s.listId) ? P.set(s.listId, (P.get(s.listId) ?? 0) + 1) : P.set(s.listId, 0));
			let ae = this.position.setSurroundPosition({
				pageNo: O,
				rowElement: z,
				row: t,
				rowElementRect: {
					x: E,
					y: D,
					height: R,
					width: l.width
				},
				availableWidth: L,
				surroundElementList: d
			});
			E = ae.x, V += ae.rowIncreaseWidth, E += l.width;
			let oe = s.type === H.SEPARATOR || s.type === H.TABLE || B?.type === H.TABLE || B?.type === H.BLOCK || s.type === H.BLOCK || B?.type === H.PAGE_BREAK || B?.imgDisplay === r.INLINE || s.imgDisplay === r.INLINE || B?.listId !== s.listId || B?.areaId !== s.areaId && !(s.area?.hide && !this.isAreaHideDisabled()) || s.control?.flexDirection === a.COLUMN && (s.controlComponent === K.CHECKBOX || s.controlComponent === K.RADIO) && B?.controlComponent === K.VALUE || e !== 0 && s.value === "​" && !(s.area?.hide && !this.isAreaHideDisabled()), se = V > L, ce = oe || se;
			if (ce) {
				let r = {
					width: l.width,
					height: R,
					startIndex: e,
					elementList: [z],
					ascent: re,
					rowIndex: t.rowIndex + 1,
					rowFlex: n[e]?.rowFlex || n[e + 1]?.rowFlex,
					isPageBreak: s.type === H.PAGE_BREAK,
					...T ? { columnIndex: I } : {}
				};
				if (r.isPageBreak && s.paperDirection && (r.paperDirection = s.paperDirection), z.controlComponent !== K.PREFIX && z.control?.indentation === Dt.VALUE_START) {
					let e = t.elementList.findIndex((e) => e.controlId === z.controlId && e.controlComponent !== K.PREFIX);
					if (~e) {
						let n = this.position.computeRowPosition({
							row: t,
							innerWidth: j
						})[e];
						n && (r.offsetX = n.coordinate.leftTop[0]);
					}
				}
				s.listId && (r.isList = !0, r.offsetX = (S.get(s.listId) || 0) + (s.listLevel ? this.listParticle.LIST_INDENT_WIDTH * s.listLevel * p : 0), r.listIndex = P.get(s.listId) ?? 0), r.offsetY = !o && s.area?.top && s.areaId !== n[e - 1]?.areaId ? s.area.top * p : 0, C.push(r);
			} else t.width += l.width, e === 0 && (Rn(n[1]) || n[1]?.areaId) ? (t.height = b, t.ascent = b) : t.height < R && (t.height = R, t.ascent = re), t.elementList.push(z);
			if (ce || e === n.length - 1) {
				if (!this.isDesignMode() && t.height > 0) {
					let e = t.elementList.filter((e) => e.value !== "​");
					e.length > 0 && e.every((e) => e.hide || e.control?.hide || e.area?.hide && !this.isAreaHideDisabled() || this.traceParticle.isTraceHidden(e)) && (t.height = 0);
				}
				if (t.isWidthNotEnough = se && !oe, !t.isSurround && (B?.rowFlex === u.JUSTIFY || B?.rowFlex === u.ALIGNMENT && t.isWidthNotEnough)) {
					let e = t.elementList[0]?.value === "​" ? t.elementList.slice(1) : t.elementList, n = (L - t.width) / (e.length - 1);
					for (let t = 0; t < e.length - 1; t++) {
						let r = e[t];
						r.metrics.width += n;
					}
					t.width = L;
				}
			}
			if (ce) {
				let e = w && w.offsets[I] || 0;
				if (E = M + e, D += t.height, i && !o && N) {
					let e = s.type === H.PAGE_BREAK, t = s.paperDirection || this.options.paperDirection;
					e && t !== k && (k = t, A = this.getMargins(k), j = this.getWidth(k) - A[1] - A[3], M = A[3], N = this.getHeight(k), w = this.columnManager.getLayout(k), T = !!w && w.count > 1);
					let n = this.getMainOuterHeight(O, k);
					(D - ee + n + R > N || e) && (!e && T && w && I < w.count - 1 ? (I += 1, D = ee, E = M + (w.offsets[I] || 0)) : (Vn(d, O), O += 1, I = 0, ee = A[0] + this.getHeader().getExtraHeight(O), D = ee, E = M + (w && w.offsets[0] || 0)));
				}
				let n = C[C.length - 1];
				n && T && n.columnIndex !== void 0 && (n.columnIndex = I), z.left = 0, E = this.position.setSurroundPosition({
					pageNo: O,
					rowElement: z,
					row: n,
					rowElementRect: {
						x: E,
						y: D,
						height: R,
						width: l.width
					},
					availableWidth: L,
					surroundElementList: d
				}).x, E += l.width;
			}
		}
		return C;
	}
	_computePageList() {
		let e = [[]], { pageMode: t, pageNumber: { maxPageNo: n } } = this.options, r = this.getHeight(), i = 0;
		if (t === h.CONTINUITY) {
			this.pageDirectionList = [this.options.paperDirection];
			let t = this.getMainOuterHeight(0);
			e[0] = this.rowList, t += this.rowList.reduce((e, t) => e + t.height + (t.offsetY || 0), 0);
			let n = this.getPagePixelRatio(), i = this.pageList[0], a = Number(i.style.height.replace("px", ""));
			if (t > a) i.style.height = `${t}px`, i.height = t * n;
			else {
				let e = t < r ? r : t;
				i.style.height = `${e}px`, i.height = e * n;
			}
			this._initPageContext(this.ctxList[0]);
		} else {
			let t = [this.options.paperDirection], r = this.options.paperDirection, a = this.getHeight(r), o = this.getMainOuterHeight(0, r), s;
			for (let c = 0; c < this.rowList.length; c++) {
				let l = this.rowList[c], u = l.offsetY || 0;
				if (s !== void 0 && l.columnIndex !== void 0 && l.columnIndex > 0 && l.columnIndex !== s) o = this.getMainOuterHeight(i, r) + l.height + u, e[i].push(l);
				else if (l.height + u + o > a || this.rowList[c - 1]?.isPageBreak) {
					if (Number.isInteger(n) && i >= n) {
						let e = l.tableFragment, t = this.elementList[l.startIndex];
						this.elementList = e && t?.type === H.TABLE && this.tablePaging.truncateTableByFragment(t, e, this.elementList) ? this.elementList.slice(0, l.startIndex + 1) : this.elementList.slice(0, l.startIndex);
						break;
					}
					i++;
					let s = this.rowList[c - 1];
					s?.isPageBreak && (r = s.paperDirection || this.options.paperDirection, a = this.getHeight(r)), t[i] = r, o = this.getMainOuterHeight(i, r) + l.height + u, e.push([l]);
				} else o += l.height + u, e[i].push(l);
				s = l.columnIndex;
			}
			this.pageDirectionList = t;
		}
		return e;
	}
	_drawHighlight(e, t) {
		let { rowList: n, positionList: r, elementList: i } = t, a = this.getDefaultBasicRowMarginHeight(), o = this.getHighlightMarginHeight();
		for (let t = 0; t < n.length; t++) {
			let s = n[t];
			for (let t = 0; t < s.elementList.length; t++) {
				let n = s.elementList[t], c = s.elementList[t - 1], l = n.highlight || this.control.getControlHighlight(i, s.startIndex + t);
				if (l) {
					c && c.highlight && c.highlight !== n.highlight && this.highlight.render(e);
					let { coordinate: { leftTop: [i, u] } } = s.fragmentPosition || r[s.startIndex + t], d = n.left || 0;
					this.highlight.recordFillInfo(e, i - d, u + a - o, n.metrics.width + d, s.height - 2 * a + 2 * o, l);
				} else c?.highlight && this.highlight.render(e);
			}
			this.highlight.render(e);
		}
	}
	drawRow(e, t) {
		this._drawHighlight(e, t);
		let { scale: n, table: { tdPadding: i }, group: a, lineBreak: o, whiteSpace: s } = this.options, { rowList: c, pageNo: l, elementList: d, positionList: f, startIndex: m, zone: h, isDrawLineBreak: g = !o.disabled, isDrawWhiteSpace: _ = !s.disabled, isDrawRange: v = !0 } = t, y = this.isPrintMode(), b = this.isGraffitiMode(), { isCrossRowCol: x, tableId: C } = this.range.getRange(), w = m;
		for (let t = 0; t < c.length; t++) {
			let o = c[t], s = {
				x: 0,
				y: 0,
				width: 0,
				height: 0
			}, m = null;
			for (let t = 0; t < o.elementList.length; t++) {
				let c = o.elementList[t];
				o.tableFragment && (w = o.startIndex + t);
				let b = c.metrics, { ascent: C, coordinate: { leftTop: [E, D] } } = o.fragmentPosition || f[o.startIndex + t], O = o.elementList[t - 1];
				if ((c.hide || c.control?.hide || c.area?.hide && !this.isAreaHideDisabled() || this.traceParticle.isTraceHidden(c)) && !this.isDesignMode()) this.textParticle.complete();
				else if (c.type === H.IMAGE) this.textParticle.complete(), c.imgDisplay !== r.SURROUND && c.imgDisplay !== r.FLOAT_TOP && c.imgDisplay !== r.FLOAT_BOTTOM && this.imageParticle.render(e, c, E, D + C);
				else if (c.type === H.LATEX) this.textParticle.complete(), this.laTexParticle.render(e, c, E, D + C);
				else if (c.type === H.TABLE) x && (s.x = E, s.y = D, m = c), this.tableParticle.render(e, c, E, D, o.tableFragment);
				else if (c.type === H.HYPERLINK) this.textParticle.complete(), this.hyperlinkParticle.render(e, c, E, D + C);
				else if (c.type === H.LABEL) this.textParticle.complete(), this.labelParticle.render(e, c, E, D + C);
				else if (c.type === H.DATE) {
					let n = o.elementList[t + 1];
					(!O || O.dateId !== c.dateId) && this.textParticle.complete(), this.textParticle.record(e, c, E, D + C), (!n || n.dateId !== c.dateId) && this.textParticle.complete();
				} else c.type === H.SUPERSCRIPT ? (this.textParticle.complete(), this.superscriptParticle.render(e, c, E, D + C)) : c.type === H.SUBSCRIPT ? (this.underline.render(e), this.textParticle.complete(), this.subscriptParticle.render(e, c, E, D + C)) : c.type === H.SEPARATOR ? this.separatorParticle.render(e, c, E, D) : c.type === H.PAGE_BREAK ? this.mode !== p.CLEAN && !y && this.pageBreakParticle.render(e, c, E, D) : c.type === H.CHECKBOX || c.controlComponent === K.CHECKBOX ? (this.textParticle.complete(), this.checkboxParticle.render({
					ctx: e,
					x: E,
					y: D + C,
					index: t,
					row: o
				})) : c.type === H.RADIO || c.controlComponent === K.RADIO ? (this.textParticle.complete(), this.radioParticle.render({
					ctx: e,
					x: E,
					y: D + C,
					index: t,
					row: o
				})) : c.type === H.TAB ? this.textParticle.complete() : c.rowFlex === u.ALIGNMENT || c.rowFlex === u.JUSTIFY ? (this.textParticle.record(e, c, E, D + C), this.textParticle.complete()) : c.type === H.BLOCK ? (this.textParticle.complete(), this.blockParticle.render(e, l, c, E, D + C)) : (c.left && this.textParticle.complete(), this.textParticle.record(e, c, E, D + C), (c.width || c.letterSpacing || S.test(c.value)) && this.textParticle.complete());
				if (g && !y && this.mode !== p.CLEAN && !o.isWidthNotEnough && t === o.elementList.length - 1 && this.lineBreakParticle.render(e, c, E, D + o.height / 2), _ && T.test(c.value) && this.whiteSpaceParticle.render(e, c, E, D + o.height / 2), c.control?.border) {
					O?.control?.border && O.controlId !== c.controlId && this.control.drawBorder(e);
					let t = this.getElementRowMargin(c);
					this.control.recordBorderInfo(E, D + t, c.metrics.width, o.height - 2 * t);
				} else O?.control?.border && this.control.drawBorder(e);
				if (c.underline || c.control?.underline) {
					O?.type === H.SUBSCRIPT && c.type !== H.SUBSCRIPT && this.underline.render(e);
					let t = this.getElementRowMargin(c), n = c.left || 0, r = 0;
					c.type === H.SUBSCRIPT && (r = this.subscriptParticle.getOffsetY(c));
					let i = c.control?.underline ? this.options.underlineColor : c.color;
					this.underline.recordFillInfo(e, E - n, D + o.height - t + r, b.width + n, 0, i, c.textDecoration?.style);
				} else (O?.underline || O?.control?.underline) && this.underline.render(e);
				if (c.strikeout) {
					if (!c.type || Be.includes(c.type)) {
						O && (O.type === H.SUBSCRIPT && c.type !== H.SUBSCRIPT || O.type === H.SUPERSCRIPT && c.type !== H.SUPERSCRIPT || this.getElementSize(O) !== this.getElementSize(c)) && this.strikeout.render(e);
						let t = this.textParticle.measureBasisWord(e, this.getElementFont(c)), r = D + C + t.actualBoundingBoxDescent * n - b.height / 2;
						c.type === H.SUBSCRIPT ? r += this.subscriptParticle.getOffsetY(c) : c.type === H.SUPERSCRIPT && (r += this.superscriptParticle.getOffsetY(c)), this.strikeout.recordFillInfo(e, E, r, b.width);
					}
				} else O?.strikeout && this.strikeout.render(e);
				this.traceParticle.render({
					ctx: e,
					element: c,
					x: E,
					y: D,
					curRow: o,
					metrics: b,
					offsetY: C,
					scale: n
				});
				let { zone: k, startIndex: A, endIndex: j } = this.range.getRange();
				if (v && k === h && A !== j && A <= w && w <= j) {
					let e = this.position.getPositionContext();
					if (!e.isTable && !c.tdId || e.tdId === c.tdId) {
						if (A === w) {
							let e = d[A + 1];
							e && e.value === "​" && (s.x = E + b.width, s.y = D, s.height = o.height, s.width += this.options.rangeMinWidth);
						} else {
							let e = b.width;
							e === 0 && o.elementList.length === 1 && (e = this.options.rangeMinWidth), s.width || (s.x = E, s.y = D, s.height = o.height), s.width += e;
						}
					}
				}
				if (!a.disabled && c.groupIds && this.group.recordFillInfo(c, E, D, b.width, o.height), w++, c.type === H.TABLE && !c.hide && !this.traceParticle.isTraceHidden(c)) {
					let t = i[1] + i[3], r = o.tableFragment;
					if (o.repeatTdPositionList?.length) for (let { td: r, positionList: i } of o.repeatTdPositionList) this.drawRow(e, {
						elementList: r.value,
						positionList: i,
						rowList: r.rowList,
						pageNo: l,
						startIndex: 0,
						innerWidth: (r.width - t) * n,
						zone: h,
						isDrawLineBreak: g,
						isDrawRange: !1
					});
					let a = r ? this.tableParticle.getFragmentTdList(c, r) : c.trList.flatMap((e) => e.tdList);
					for (let i of a) {
						let a = i.rowList, o = 0;
						if (r) {
							let [e, t] = this.tableParticle.getTdWindowInFragment(i, c, r);
							if (t <= e) continue;
							if (e > 0 || t < i.height) {
								let n = this.tableParticle.getTdVisibleRowListByWindow(i, e, t);
								a = n.rowList, o = n.startIndex;
							}
						}
						this.drawRow(e, {
							elementList: i.value,
							positionList: i.positionList,
							rowList: a,
							pageNo: l,
							startIndex: o,
							innerWidth: (i.width - t) * n,
							zone: h,
							isDrawLineBreak: g
						});
					}
				}
			}
			if (o.isList && o.height > 0 && this.listParticle.drawListStyle(e, o, f[o.startIndex]), this.textParticle.complete(), this.control.drawBorder(e), this.underline.render(e), this.strikeout.render(e), this.traceParticle.flush(e), this.group.render(e), !y && !b) {
				if (s.width && s.height) {
					let { x: t, y: n, width: r, height: i } = s;
					this.range.render(e, t, n, r, i);
				}
				if (v && x && m && m.id === C) {
					let { coordinate: { leftTop: [t, n] } } = o.fragmentPosition || f[o.startIndex];
					this.tableParticle.drawRange(e, m, t, n, o.tableFragment);
				}
			}
		}
	}
	_drawFloat(e, t) {
		let n = this.position.getFloatPositionList(), { imgDisplays: r, pageNo: i } = t;
		for (let t = 0; t < n.length; t++) {
			let a = n[t], o = a.element;
			if ((i === a.pageNo || a.zone === m.HEADER || a.zone == m.FOOTER) && o.imgDisplay && r.includes(o.imgDisplay) && o.type === H.IMAGE) {
				let { x: t, y: n } = this.position.getFloatPositionCoordinate(a);
				this.imageParticle.render(e, o, t, n);
			}
		}
	}
	_clearPage(e) {
		let t = this.ctxList[e], n = this.pageList[e];
		t.clearRect(0, 0, Math.max(n.width, this.getWidth()), Math.max(n.height, this.getHeight())), this.blockParticle.clear();
	}
	_drawPage(e) {
		let { elementList: t, positionList: n, rowList: i, pageNo: a } = e, { inactiveAlpha: o, pageMode: s, header: c, footer: l, pageNumber: u, lineNumber: d, pageBorder: f } = this.options, g = this.mode === p.PRINT, _ = s === h.CONTINUITY, { innerWidth: v } = this.getPageSize(a), y = this.ctxList[a];
		y.globalAlpha = this.zone.isMainActive() ? 1 : o, this._clearPage(a), (!g || !this.options.modeRule[p.PRINT]?.backgroundDisabled) && this.background.render(y, a), g || this.area.render(y, a), this.columnManager.drawSeparator(y, a), !_ && this.options.watermark.data && this.options.watermark.layer === Zt.BOTTOM && this.waterMark.render(y, a), g || this.margin.render(y, a), this._drawFloat(y, {
			pageNo: a,
			imgDisplays: [r.FLOAT_BOTTOM]
		}), g || this.control.renderHighlightList(y, a);
		let b = i[0]?.startIndex;
		this.drawRow(y, {
			elementList: t,
			positionList: n,
			rowList: i,
			pageNo: a,
			startIndex: b,
			innerWidth: v,
			zone: m.MAIN
		}), this.getIsPagingMode() && (c.disabled || this.header.render(y, a), u.disabled || this.pageNumber.render(y, a), l.disabled || this.footer.render(y, a)), this._drawFloat(y, {
			pageNo: a,
			imgDisplays: [r.FLOAT_TOP, r.SURROUND]
		}), !g && this.search.getSearchKeyword() && this.search.render(y, a), !g && this.spellcheck.getSpellcheckRangeList().length && this.spellcheck.render(y, a), this.elementList.length <= 1 && !this.elementList[0]?.listId && this.placeholder.render(y), d.disabled || this.lineNumber.render(y, a), f.disabled || this.pageBorder.render(y, a), this.badge.render(y, a), this.isGraffitiMode() && this.graffiti.render(y, a), !_ && this.options.watermark.data && this.options.watermark.layer === Zt.TOP && this.waterMark.render(y, a);
	}
	_disconnectLazyRender() {
		this.lazyRenderIntersectionObserver?.disconnect();
	}
	_lazyRender() {
		let e = this.position.getOriginalMainPositionList(), t = this.getOriginalMainElementList();
		this._disconnectLazyRender(), this.lazyRenderIntersectionObserver = new IntersectionObserver((n) => {
			n.forEach((n) => {
				if (n.isIntersecting) {
					let r = Number(n.target.dataset.index);
					this._drawPage({
						elementList: t,
						positionList: e,
						rowList: this.pageRowList[r],
						pageNo: r
					});
				}
			});
		}), this.pageList.forEach((e) => {
			this.lazyRenderIntersectionObserver.observe(e);
		});
	}
	_immediateRender() {
		let e = this.position.getOriginalMainPositionList(), t = this.getOriginalMainElementList();
		for (let n = 0; n < this.pageRowList.length; n++) this._drawPage({
			elementList: t,
			positionList: e,
			rowList: this.pageRowList[n],
			pageNo: n
		});
	}
	render(e) {
		this.renderCount++;
		let { header: t, footer: n } = this.options, { isSubmitHistory: r = !0, isSetCursor: i = !0, isCompute: a = !0, isLazy: o = !0, isInit: s = !1, isSourceHistory: c = !1, isFirstRender: l = !1 } = e || {}, { curIndex: u } = e || {}, d = this.getInnerWidth(), f = this.getIsPagingMode(), p = this.pageRowList.length, m = this.pageDirectionList;
		if (a) {
			this.spellcheck.setSpellcheckRangeList(null), this.position.setFloatPositionList([]), f && (this.columnManager.compute(), t.disabled || this.header.compute(), n.disabled || this.footer.compute());
			let e = this.getMargins(), r = this.getHeight(), i = this.header.getExtraHeight(), a = e[3], o = e[0] + i, s = Bn(this.elementList);
			if (this.rowList = this.computeRowList({
				startX: a,
				startY: o,
				pageHeight: r,
				isPagingMode: f,
				innerWidth: d,
				surroundElementList: s,
				elementList: this.elementList
			}), f && (this.rowList = this.tablePaging.splitTableRowAcrossPages(this.rowList)), this.pageRowList = this._computePageList(), this.position.computePositionList(), this.area.compute(), !this.isPrintMode()) {
				let e = this.search.getSearchKeyword();
				e && this.search.compute(e), this.control.computeHighlightList();
			}
			this.isGraffitiMode() && this.graffiti.compute();
		}
		this.imageObserver.clearAll(), this.cursor.recoveryCursor();
		for (let e = 0; e < this.pageRowList.length; e++) this.pageList[e] || this._createPage(e);
		let h = this.pageRowList.length, g = this.pageList.length;
		if (g > h) {
			let e = g - h;
			this.ctxList.splice(h, e), this.pageList.splice(h, e).forEach((e) => e.remove());
		}
		(m.length !== this.pageDirectionList.length || m.some((e, t) => e !== this.pageDirectionList[t])) && this._updatePageSizes(), o && f ? this._lazyRender() : this._immediateRender(), i ? u = this.setCursor(u) : this.range.getIsSelection() && this.cursor.focus(), (r && !l || u !== void 0 && this.historyManager.isStackEmpty()) && this.submitHistory(u), a && this.eventBus.isSubscribe("renderChange") && this.eventBus.emit("renderChange"), R(() => {
			this.range.setRangeStyle(), a && this.control.getActiveControl() && this.control.reAwakeControl(), a && !this.isReadonly() && this.position.getPositionContext().isTable && this.tableTool.render(), a && !this.zone.isMainActive() && this.zone.drawZoneIndicator(), a && this.ruler.render(), p !== this.pageRowList.length && (this.listener.pageSizeChange && this.listener.pageSizeChange(this.pageRowList.length), this.eventBus.isSubscribe("pageSizeChange") && this.eventBus.emit("pageSizeChange", this.pageRowList.length)), (r || c) && !s && (this.listener.contentChange && this.listener.contentChange(), this.eventBus.isSubscribe("contentChange") && this.eventBus.emit("contentChange"));
		});
	}
	setCursor(e) {
		let t = this.position.getPositionContext(), n = this.position.getPositionList();
		if (t.isTable) {
			let n = this.getOriginalElementList(), r = this.position.getTableTdByContext(n, t)?.positionList;
			r?.length && (e === void 0 || e > r.length - 1) && (e = r.length - 1);
			let i = r?.[e];
			this.position.setCursorPosition(i || null), this.tableTool.render();
		} else this.position.setCursorPosition(e === void 0 ? null : n[e]);
		let r = !0;
		if (e !== void 0 && t.isImage && t.isDirectHit) {
			let t = this.getElementList()[e];
			if (Ve.includes(t.type)) {
				r = !1;
				let e = this.position.getCursorPosition();
				this.previewer.updateResizer(t, e);
			}
		}
		return this.cursor.drawCursor({ isShow: r }), e;
	}
	submitHistory(e) {
		// TomeLinea diagnostic 2.36I :
		// désactivation temporaire de la copie complète du document à chaque frappe.
		// But unique : mesurer si l'historique Canvas est responsable de la latence.
		return;
	}
	destroy() {
		this.container.remove(), this.globalEvent.removeEvent(), this.scrollObserver.removeEvent(), this.selectionObserver.removeEvent(), this.workerManager.destroy(), this.magnifier.destroy(), this.accessibility.destroy(), this.ruler.dispose(), this.lazyRenderIntersectionObserver?.disconnect();
	}
	clearSideEffect() {
		this.getPreviewer().clearResizer(), this.getTableTool().dispose(), this.getHyperlinkParticle().clearHyperlinkPopup(), this.getHintParticle().clearHintPopup(), this.getTraceParticle().clearTracePopup(), this.getDateParticle().clearDatePicker();
	}
}, so = class {
	executeMode;
	executeCut;
	executeCopy;
	executePaste;
	executeSelectAll;
	executeBackspace;
	executeSetRange;
	executeReplaceRange;
	executeSetPositionContext;
	executeForceUpdate;
	executeBlur;
	executeHideCursor;
	executeUndo;
	executeRedo;
	executePainter;
	executeApplyPainterStyle;
	executeFormat;
	executeFont;
	executeSize;
	executeSizeAdd;
	executeSizeMinus;
	executeBold;
	executeItalic;
	executeUnderline;
	executeStrikeout;
	executeSuperscript;
	executeSubscript;
	executeColor;
	executeHighlight;
	executeTitle;
	executeList;
	executeRowFlex;
	executeRowMargin;
	executeInsertTable;
	executeInsertTableTopRow;
	executeInsertTableBottomRow;
	executeInsertTableLeftCol;
	executeInsertTableRightCol;
	executeDeleteTableRow;
	executeDeleteTableCol;
	executeDeleteTable;
	executeMergeTableCell;
	executeCancelMergeTableCell;
	executeSplitVerticalTableCell;
	executeSplitHorizontalTableCell;
	executeTableTdVerticalAlign;
	executeTableBorderType;
	executeTableBorderColor;
	executeTableTdBorderType;
	executeTableTdSlashType;
	executeTableTdBackgroundColor;
	executeTableAutoFitToContent;
	executeTableAutoFitToPage;
	executeTableSelectAll;
	executeImage;
	executeHyperlink;
	executeDeleteHyperlink;
	executeCancelHyperlink;
	executeEditHyperlink;
	executeSeparator;
	executePageBreak;
	executeAddWatermark;
	executeDeleteWatermark;
	executeSearch;
	executeSetSpellcheckRangeList;
	executeSearchNavigatePre;
	executeSearchNavigateNext;
	executeReplace;
	executePrint;
	executeReplaceImageElement;
	executeSaveAsImageElement;
	executeSetImageCrop;
	executeSetImageCaption;
	executeChangeImageDisplay;
	executePageMode;
	executeSetColumns;
	executePageScale;
	executePageScaleRecovery;
	executePageScaleMinus;
	executePageScaleAdd;
	executePaperSize;
	executePaperDirection;
	executePageDirection;
	executeSetPaperMargin;
	executeSetMainBadge;
	executeSetAreaBadge;
	executeInsertElementList;
	executeInsertArea;
	executeSetAreaValue;
	executeSetAreaProperties;
	executeDeleteArea;
	executeLocationArea;
	executeClearGraffiti;
	executeToggleTrace;
	executeCompare;
	executeToggleRuler;
	executeAppendElementList;
	executeUpdateElementById;
	executeDeleteElementById;
	executeSetValue;
	executeRemoveControl;
	executeTranslate;
	executeSetLocale;
	executeLocationCatalog;
	executeWordTool;
	executeSetHTML;
	executeSetGroup;
	executeDeleteGroup;
	executeLocationGroup;
	executeSetZone;
	executeSetControlValue;
	executeSetControlValueList;
	executeSetControlExtension;
	executeSetControlExtensionList;
	executeSetControlProperties;
	executeSetControlPropertiesList;
	executeSetControlHighlight;
	executeValidate;
	executeClearValidate;
	executeLocationControl;
	executeInsertControl;
	executeJumpControl;
	executeUpdateOptions;
	executeInsertTitle;
	executeFocus;
	executeComputeElementListHeight;
	getCatalog;
	getImage;
	getOptions;
	getValue;
	getValueAsync;
	getAreaValue;
	getHTML;
	getText;
	getSpellcheckWordList;
	getWordCount;
	getCursorPosition;
	getRemainingContentHeight;
	getRange;
	getRangeText;
	getRangeContext;
	getRangeRow;
	getRangeParagraph;
	getKeywordRangeList;
	getKeywordContext;
	getPaperMargin;
	getColumns;
	getSearchNavigateInfo;
	getLocale;
	getGroupIds;
	getGroupRectList;
	getControlValue;
	getControlList;
	getContainer;
	getTitleValue;
	getPositionContextByEvent;
	getElementById;
	interceptor;
	setInterceptor(e) {
		this.interceptor = e;
	}
	wrap(e, t) {
		return ((...n) => (this.interceptor?.(e, n), t(...n)));
	}
	constructor(e) {
		this.executeMode = this.wrap("executeMode", e.mode.bind(e)), this.executeCut = this.wrap("executeCut", e.cut.bind(e)), this.executeCopy = this.wrap("executeCopy", e.copy.bind(e)), this.executePaste = this.wrap("executePaste", e.paste.bind(e)), this.executeSelectAll = this.wrap("executeSelectAll", e.selectAll.bind(e)), this.executeBackspace = this.wrap("executeBackspace", e.backspace.bind(e)), this.executeSetRange = this.wrap("executeSetRange", e.setRange.bind(e)), this.executeReplaceRange = this.wrap("executeReplaceRange", e.replaceRange.bind(e)), this.executeSetPositionContext = this.wrap("executeSetPositionContext", e.setPositionContext.bind(e)), this.executeForceUpdate = this.wrap("executeForceUpdate", e.forceUpdate.bind(e)), this.executeBlur = this.wrap("executeBlur", e.blur.bind(e)), this.executeHideCursor = this.wrap("executeHideCursor", e.hideCursor.bind(e)), this.executeUndo = this.wrap("executeUndo", e.undo.bind(e)), this.executeRedo = this.wrap("executeRedo", e.redo.bind(e)), this.executePainter = this.wrap("executePainter", e.painter.bind(e)), this.executeApplyPainterStyle = this.wrap("executeApplyPainterStyle", e.applyPainterStyle.bind(e)), this.executeFormat = this.wrap("executeFormat", e.format.bind(e)), this.executeFont = this.wrap("executeFont", e.font.bind(e)), this.executeSize = this.wrap("executeSize", e.size.bind(e)), this.executeSizeAdd = this.wrap("executeSizeAdd", e.sizeAdd.bind(e)), this.executeSizeMinus = this.wrap("executeSizeMinus", e.sizeMinus.bind(e)), this.executeBold = this.wrap("executeBold", e.bold.bind(e)), this.executeItalic = this.wrap("executeItalic", e.italic.bind(e)), this.executeUnderline = this.wrap("executeUnderline", e.underline.bind(e)), this.executeStrikeout = this.wrap("executeStrikeout", e.strikeout.bind(e)), this.executeSuperscript = this.wrap("executeSuperscript", e.superscript.bind(e)), this.executeSubscript = this.wrap("executeSubscript", e.subscript.bind(e)), this.executeColor = this.wrap("executeColor", e.color.bind(e)), this.executeHighlight = this.wrap("executeHighlight", e.highlight.bind(e)), this.executeTitle = this.wrap("executeTitle", e.title.bind(e)), this.executeList = this.wrap("executeList", e.list.bind(e)), this.executeRowFlex = this.wrap("executeRowFlex", e.rowFlex.bind(e)), this.executeRowMargin = this.wrap("executeRowMargin", e.rowMargin.bind(e)), this.executeInsertTable = this.wrap("executeInsertTable", e.insertTable.bind(e)), this.executeInsertTableTopRow = this.wrap("executeInsertTableTopRow", e.insertTableTopRow.bind(e)), this.executeInsertTableBottomRow = this.wrap("executeInsertTableBottomRow", e.insertTableBottomRow.bind(e)), this.executeInsertTableLeftCol = this.wrap("executeInsertTableLeftCol", e.insertTableLeftCol.bind(e)), this.executeInsertTableRightCol = this.wrap("executeInsertTableRightCol", e.insertTableRightCol.bind(e)), this.executeDeleteTableRow = this.wrap("executeDeleteTableRow", e.deleteTableRow.bind(e)), this.executeDeleteTableCol = this.wrap("executeDeleteTableCol", e.deleteTableCol.bind(e)), this.executeDeleteTable = this.wrap("executeDeleteTable", e.deleteTable.bind(e)), this.executeMergeTableCell = this.wrap("executeMergeTableCell", e.mergeTableCell.bind(e)), this.executeCancelMergeTableCell = this.wrap("executeCancelMergeTableCell", e.cancelMergeTableCell.bind(e)), this.executeSplitVerticalTableCell = this.wrap("executeSplitVerticalTableCell", e.splitVerticalTableCell.bind(e)), this.executeSplitHorizontalTableCell = this.wrap("executeSplitHorizontalTableCell", e.splitHorizontalTableCell.bind(e)), this.executeTableTdVerticalAlign = this.wrap("executeTableTdVerticalAlign", e.tableTdVerticalAlign.bind(e)), this.executeTableBorderType = this.wrap("executeTableBorderType", e.tableBorderType.bind(e)), this.executeTableBorderColor = this.wrap("executeTableBorderColor", e.tableBorderColor.bind(e)), this.executeTableTdBorderType = this.wrap("executeTableTdBorderType", e.tableTdBorderType.bind(e)), this.executeTableTdSlashType = this.wrap("executeTableTdSlashType", e.tableTdSlashType.bind(e)), this.executeTableTdBackgroundColor = this.wrap("executeTableTdBackgroundColor", e.tableTdBackgroundColor.bind(e)), this.executeTableAutoFitToContent = this.wrap("executeTableAutoFitToContent", e.tableAutoFitToContent.bind(e)), this.executeTableAutoFitToPage = this.wrap("executeTableAutoFitToPage", e.tableAutoFitToPage.bind(e)), this.executeTableSelectAll = this.wrap("executeTableSelectAll", e.tableSelectAll.bind(e)), this.executeImage = this.wrap("executeImage", e.image.bind(e)), this.executeHyperlink = this.wrap("executeHyperlink", e.hyperlink.bind(e)), this.executeDeleteHyperlink = this.wrap("executeDeleteHyperlink", e.deleteHyperlink.bind(e)), this.executeCancelHyperlink = this.wrap("executeCancelHyperlink", e.cancelHyperlink.bind(e)), this.executeEditHyperlink = this.wrap("executeEditHyperlink", e.editHyperlink.bind(e)), this.executeSeparator = this.wrap("executeSeparator", e.separator.bind(e)), this.executePageBreak = this.wrap("executePageBreak", e.pageBreak.bind(e)), this.executeAddWatermark = this.wrap("executeAddWatermark", e.addWatermark.bind(e)), this.executeDeleteWatermark = this.wrap("executeDeleteWatermark", e.deleteWatermark.bind(e)), this.executeSearch = this.wrap("executeSearch", e.search.bind(e)), this.executeSetSpellcheckRangeList = this.wrap("executeSetSpellcheckRangeList", e.setSpellcheckRangeList.bind(e)), this.executeSearchNavigatePre = this.wrap("executeSearchNavigatePre", e.searchNavigatePre.bind(e)), this.executeSearchNavigateNext = this.wrap("executeSearchNavigateNext", e.searchNavigateNext.bind(e)), this.executeReplace = this.wrap("executeReplace", e.replace.bind(e)), this.executePrint = this.wrap("executePrint", e.print.bind(e)), this.executeReplaceImageElement = this.wrap("executeReplaceImageElement", e.replaceImageElement.bind(e)), this.executeSaveAsImageElement = this.wrap("executeSaveAsImageElement", e.saveAsImageElement.bind(e)), this.executeSetImageCrop = this.wrap("executeSetImageCrop", e.setImageCrop.bind(e)), this.executeSetImageCaption = this.wrap("executeSetImageCaption", e.setImageCaption.bind(e)), this.executeChangeImageDisplay = this.wrap("executeChangeImageDisplay", e.changeImageDisplay.bind(e)), this.executePageMode = this.wrap("executePageMode", e.pageMode.bind(e)), this.executeSetColumns = this.wrap("executeSetColumns", e.setColumns.bind(e)), this.executePageScale = this.wrap("executePageScale", e.pageScale.bind(e)), this.executePageScaleRecovery = this.wrap("executePageScaleRecovery", e.pageScaleRecovery.bind(e)), this.executePageScaleMinus = this.wrap("executePageScaleMinus", e.pageScaleMinus.bind(e)), this.executePageScaleAdd = this.wrap("executePageScaleAdd", e.pageScaleAdd.bind(e)), this.executePaperSize = this.wrap("executePaperSize", e.paperSize.bind(e)), this.executePaperDirection = this.wrap("executePaperDirection", e.paperDirection.bind(e)), this.executePageDirection = this.wrap("executePageDirection", e.pageDirection.bind(e)), this.executeSetPaperMargin = this.wrap("executeSetPaperMargin", e.setPaperMargin.bind(e)), this.executeSetMainBadge = this.wrap("executeSetMainBadge", e.setMainBadge.bind(e)), this.executeSetAreaBadge = this.wrap("executeSetAreaBadge", e.setAreaBadge.bind(e)), this.getAreaValue = e.getAreaValue.bind(e), this.executeInsertArea = this.wrap("executeInsertArea", e.insertArea.bind(e)), this.executeSetAreaValue = this.wrap("executeSetAreaValue", e.setAreaValue.bind(e)), this.executeSetAreaProperties = this.wrap("executeSetAreaProperties", e.setAreaProperties.bind(e)), this.executeDeleteArea = this.wrap("executeDeleteArea", e.deleteArea.bind(e)), this.executeLocationArea = this.wrap("executeLocationArea", e.locationArea.bind(e)), this.executeClearGraffiti = this.wrap("executeClearGraffiti", e.clearGraffiti.bind(e)), this.executeToggleTrace = this.wrap("executeToggleTrace", e.toggleTrace.bind(e)), this.executeCompare = this.wrap("executeCompare", e.compare.bind(e)), this.executeToggleRuler = this.wrap("executeToggleRuler", e.toggleRuler.bind(e)), this.executeInsertElementList = this.wrap("executeInsertElementList", e.insertElementList.bind(e)), this.executeAppendElementList = this.wrap("executeAppendElementList", e.appendElementList.bind(e)), this.executeUpdateElementById = this.wrap("executeUpdateElementById", e.updateElementById.bind(e)), this.executeDeleteElementById = this.wrap("executeDeleteElementById", e.deleteElementById.bind(e)), this.executeSetValue = this.wrap("executeSetValue", e.setValue.bind(e)), this.executeRemoveControl = this.wrap("executeRemoveControl", e.removeControl.bind(e)), this.executeTranslate = this.wrap("executeTranslate", e.translate.bind(e)), this.executeSetLocale = this.wrap("executeSetLocale", e.setLocale.bind(e)), this.executeLocationCatalog = this.wrap("executeLocationCatalog", e.locationCatalog.bind(e)), this.executeWordTool = this.wrap("executeWordTool", e.wordTool.bind(e)), this.executeSetHTML = this.wrap("executeSetHTML", e.setHTML.bind(e)), this.executeSetGroup = this.wrap("executeSetGroup", e.setGroup.bind(e)), this.executeDeleteGroup = this.wrap("executeDeleteGroup", e.deleteGroup.bind(e)), this.executeLocationGroup = this.wrap("executeLocationGroup", e.locationGroup.bind(e)), this.executeSetZone = this.wrap("executeSetZone", e.setZone.bind(e)), this.executeUpdateOptions = this.wrap("executeUpdateOptions", e.updateOptions.bind(e)), this.executeInsertTitle = this.wrap("executeInsertTitle", e.insertTitle.bind(e)), this.executeFocus = this.wrap("executeFocus", e.focus.bind(e)), this.executeComputeElementListHeight = this.wrap("executeComputeElementListHeight", e.computeElementListHeight.bind(e)), this.getImage = e.getImage.bind(e), this.getOptions = e.getOptions.bind(e), this.getValue = e.getValue.bind(e), this.getValueAsync = e.getValueAsync.bind(e), this.getHTML = e.getHTML.bind(e), this.getText = e.getText.bind(e), this.getSpellcheckWordList = e.getSpellcheckWordList.bind(e), this.getWordCount = e.getWordCount.bind(e), this.getCursorPosition = e.getCursorPosition.bind(e), this.getRemainingContentHeight = e.getRemainingContentHeight.bind(e), this.getRange = e.getRange.bind(e), this.getRangeText = e.getRangeText.bind(e), this.getRangeContext = e.getRangeContext.bind(e), this.getRangeRow = e.getRangeRow.bind(e), this.getRangeParagraph = e.getRangeParagraph.bind(e), this.getKeywordRangeList = e.getKeywordRangeList.bind(e), this.getKeywordContext = e.getKeywordContext.bind(e), this.getCatalog = e.getCatalog.bind(e), this.getPaperMargin = e.getPaperMargin.bind(e), this.getColumns = e.getColumns.bind(e), this.getSearchNavigateInfo = e.getSearchNavigateInfo.bind(e), this.getLocale = e.getLocale.bind(e), this.getGroupIds = e.getGroupIds.bind(e), this.getGroupRectList = e.getGroupRectList.bind(e), this.getContainer = e.getContainer.bind(e), this.getTitleValue = e.getTitleValue.bind(e), this.getPositionContextByEvent = e.getPositionContextByEvent.bind(e), this.getElementById = e.getElementById.bind(e), this.executeSetControlValue = this.wrap("executeSetControlValue", e.setControlValue.bind(e)), this.executeSetControlValueList = this.wrap("executeSetControlValueList", e.setControlValueList.bind(e)), this.executeSetControlExtension = this.wrap("executeSetControlExtension", e.setControlExtension.bind(e)), this.executeSetControlExtensionList = this.wrap("executeSetControlExtensionList", e.setControlExtensionList.bind(e)), this.executeSetControlProperties = this.wrap("executeSetControlProperties", e.setControlProperties.bind(e)), this.executeSetControlPropertiesList = this.wrap("executeSetControlPropertiesList", e.setControlPropertiesList.bind(e)), this.executeSetControlHighlight = this.wrap("executeSetControlHighlight", e.setControlHighlight.bind(e)), this.executeValidate = this.wrap("executeValidate", e.validate.bind(e)), this.executeClearValidate = this.wrap("executeClearValidate", e.clearValidate.bind(e)), this.getControlValue = e.getControlValue.bind(e), this.getControlList = e.getControlList.bind(e), this.executeLocationControl = this.wrap("executeLocationControl", e.locationControl.bind(e)), this.executeInsertControl = this.wrap("executeInsertControl", e.insertControl.bind(e)), this.executeJumpControl = this.wrap("executeJumpControl", e.jumpControl.bind(e));
	}
};
//#endregion
//#region src/editor/utils/paragraph.ts
function co(e, t) {
	let n = 0;
	for (let r = 1; r < t; r++) {
		let t = e[r], i = e[r - 1];
		(t.value === "​" && !t.listWrap && !t.listId || t.listId !== i?.listId && i.value !== "​" || t.titleId !== i?.titleId && i.value !== "​") && n++;
	}
	return n;
}
//#endregion
//#region src/editor/utils/print.ts
function lo(e, t) {
	return e === 1125 && t === 1593 ? {
		size: "a3",
		width: "297mm",
		height: "420mm"
	} : e === 794 && t === 1123 ? {
		size: "a4",
		width: "210mm",
		height: "297mm"
	} : e === 565 && t === 796 ? {
		size: "a5",
		width: "148mm",
		height: "210mm"
	} : {
		size: "",
		width: `${e}px`,
		height: `${t}px`
	};
}
async function uo(e, t) {
	let { width: n, height: r, direction: i = g.VERTICAL, pageDirections: a, iframeInfoList: o = [] } = t, s = document.createElement("iframe");
	s.style.visibility = "hidden", s.style.position = "absolute", s.style.left = "0", s.style.top = "0", s.style.width = "0", s.style.height = "0", s.style.border = "none", document.body.append(s);
	let c = s.contentWindow, l = c.document;
	l.open();
	let u = document.createElement("div"), d = lo(n, r), f = (e) => a?.[e] || i, p = f(0), m = f(e.length - 1), h = e.some((e, t) => f(t) !== p);
	e.forEach((t, n) => {
		let r = f(n), i = document.createElement("div");
		i.style.position = "relative", i.style.width = r === g.HORIZONTAL ? d.height : d.width, i.style.height = r === g.HORIZONTAL ? d.width : d.height, h && n < e.length - 1 && i.style.setProperty("page", r === g.HORIZONTAL ? "canvas-editor-landscape" : "canvas-editor-portrait");
		let a = document.createElement("img");
		a.style.width = "100%", a.style.height = "100%", a.style.position = "absolute", a.style.left = "0", a.style.top = "0", a.src = t, i.append(a), (o[n] || []).forEach((e) => {
			let t = document.createElement("iframe");
			if (t.style.position = "absolute", t.style.left = `${e.x}px`, t.style.top = `${e.y}px`, t.style.width = `${e.width}px`, t.style.height = `${e.height}px`, t.style.border = "none", e.src) t.src = e.src;
			else if (e.srcdoc) {
				let n = "\n        <script>\n          if (!window.__CUSTOM_CANVAS_EDITOR_LOAD_HOOK__) {\n            window.postMessage({ type: '__LOADED_TO_CANVAS_EDITOR__' }, '*')\n          }\n        <\/script>", r = e.srcdoc;
				t.srcdoc = r.includes("</body>") ? r.replace("</body>", `${n}</body>`) : r + n;
			}
			i.append(t);
		}), u.append(i);
	});
	let _ = document.createElement("style"), v = `
  * {
    margin: 0;
    padding: 0;
  }${h ? `
  @page {
    margin: 0;
    size: ${d.size} ${m === g.HORIZONTAL ? "landscape" : "portrait"};
  }
  @page canvas-editor-portrait {
    margin: 0;
    size: ${d.size} portrait;
  }
  @page canvas-editor-landscape {
    margin: 0;
    size: ${d.size} landscape;
  }` : `
  @page {
    margin: 0;
    size: ${d.size} ${p === g.HORIZONTAL ? "landscape" : "portrait"};
  }`}`;
	_.append(document.createTextNode(v)), l.write(`${_.outerHTML}${u.innerHTML}`), o.length && await fo(l), setTimeout(async () => {
		c.print(), l.close(), window.addEventListener("mouseover", () => {
			s?.remove();
		}, { once: !0 });
	});
}
async function fo(e) {
	let t = Array.from(e.querySelectorAll("iframe")).map((e) => new Promise((t) => {
		e.srcdoc ? e.contentWindow?.addEventListener("message", (e) => {
			e.data.type === "__LOADED_TO_CANVAS_EDITOR__" && t(!0);
		}) : t(!0);
	}));
	await Promise.allSettled(t);
}
//#endregion
//#region src/editor/utils/diff.ts
function po(e, t, n) {
	if (!n) return;
	let r = e[e.length - 1];
	r && r.type === t ? r.value += n : e.push({
		type: t,
		value: n
	});
}
function mo(e, t) {
	let n = e.length, r = t.length, i = Math.ceil((n + r) / 2), a = n - r, o = i, s = Array(2 * i + 1).fill(0), c = Array(2 * i + 1).fill(0);
	for (let l = 0; l <= i; l++) {
		for (let i = -l; i <= l; i += 2) {
			let u = i === -l || i !== l && s[i - 1 + o] < s[i + 1 + o] ? s[i + 1 + o] : s[i - 1 + o] + 1, d = u - i, f = u, p = d;
			for (; u < n && d < r && e[u] === t[d];) u++, d++;
			if (s[i + o] = u, a % 2 != 0) {
				let e = i - a;
				if (e >= 1 - l && e <= l - 1 && u + c[e + o] >= n) return {
					x: f,
					y: p,
					u,
					v: d,
					d: 2 * l - 1
				};
			}
		}
		for (let i = -l; i <= l; i += 2) {
			let u;
			u = i === l ? c[i - 1 + o] : i === -l ? c[i + 1 + o] + 1 : Math.max(c[i - 1 + o], c[i + 1 + o] + 1);
			let d = u + i, f = u, p = d;
			for (; u < n && d >= 0 && d < r && e[n - 1 - u] === t[r - 1 - d];) u++, d++;
			if (c[i + o] = u, a % 2 == 0) {
				let e = i + a;
				if (e >= -l && e <= l && u + s[e + o] >= n) return {
					x: n - u,
					y: r - d,
					u: n - f,
					v: r - p,
					d: 2 * l
				};
			}
		}
	}
	return {
		x: 0,
		y: 0,
		u: n,
		v: r,
		d: n + r
	};
}
function ho(e, t, n, r, i, a, o) {
	let s = 0;
	for (; t + s < n && i + s < a && e[t + s] === r[i + s];) s++;
	s && po(o, "equal", e.slice(t, t + s).join("")), t += s, i += s;
	let c = 0;
	for (; n - 1 - c >= t && a - 1 - c >= i && e[n - 1 - c] === r[a - 1 - c];) c++;
	let l = n - c, u = a - c;
	if (t >= l) po(o, "insert", r.slice(i, u).join(""));
	else if (i >= u) po(o, "delete", e.slice(t, l).join(""));
	else {
		let n = e.slice(t, l), a = r.slice(i, u), s = mo(n, a);
		s.d <= 1 ? (po(o, "delete", n.join("")), po(o, "insert", a.join(""))) : (ho(e, t, t + s.x, r, i, i + s.y, o), (s.u !== s.x || s.v !== s.y) && po(o, "equal", n.slice(s.x, s.u).join("")), ho(e, t + s.u, l, r, i + s.v, u, o));
	}
	c && po(o, "equal", e.slice(l, n).join(""));
}
function go(e, t) {
	let n = [...e], r = [...t], i = [];
	return ho(n, 0, n.length, r, 0, r.length, i), i;
}
function _o(e) {
	let t = e.split("\n");
	return t.map((e, n) => n < t.length - 1 ? `${e}\n` : e);
}
function vo(e, t) {
	if (e === t) return 1;
	if (!e.length || !t.length) return 0;
	let n = (n) => {
		if (e.length < n || t.length < n) return 0;
		let r = /* @__PURE__ */ new Map();
		for (let t = 0; t <= e.length - n; t++) {
			let i = e.slice(t, t + n);
			r.set(i, (r.get(i) || 0) + 1);
		}
		let i = 0;
		for (let e = 0; e <= t.length - n; e++) {
			let a = t.slice(e, e + n), o = r.get(a) || 0;
			o > 0 && (i++, r.set(a, o - 1));
		}
		return 2 * i / (e.length - n + 1 + (t.length - n + 1));
	};
	return Math.max(n(1), n(2));
}
var yo = .5;
function bo(e, t, n) {
	let r = _o(t), i = _o(n), a = Math.max(r.length, i.length);
	for (let t = 0; t < a; t++) {
		let n = r[t], a = i[t];
		if (n !== void 0 && a !== void 0 && (n === a || vo(n, a) >= yo)) for (let t of go(n, a)) po(e, t.type, t.value);
		else n !== void 0 && po(e, "delete", n), a !== void 0 && po(e, "insert", a);
	}
}
function xo(e, t) {
	if (!e.includes("\n") && !t.includes("\n")) return go(e, t);
	let n = _o(e), r = _o(t), i = [];
	ho(n, 0, n.length, r, 0, r.length, i);
	let a = [];
	for (let e = 0; e < i.length; e++) {
		let t = i[e], n = i[e + 1];
		t.type === "delete" && n?.type === "insert" ? (bo(a, t.value, n.value), e++) : t.type === "insert" && n?.type === "delete" ? (bo(a, n.value, t.value), e++) : po(a, t.type, t.value);
	}
	return a;
}
function So(e) {
	let t = e[0], n = t.control?.conceptId || t.controlId;
	return n ? `control:${n}` : t.type === H.LIST && t.listId ? `list:${t.listId}` : t.type === H.TITLE && t.titleId ? `title:${t.titleId}` : t.type === H.HYPERLINK && t.url ? `hyperlink:${t.url}` : null;
}
function Co(e) {
	let t = [[]], n = [];
	return e.forEach((e, r) => {
		if (En(e)) {
			if (!e.value) return;
			for (let n of e.value) t[t.length - 1].push({
				elementIndex: r,
				char: n
			});
			return;
		}
		let i = n[n.length - 1];
		if (e.controlId && i && !t[t.length - 1].length && i.elements[0].controlId === e.controlId) {
			i.elements.push(e);
			return;
		}
		let a = {
			elements: [e],
			key: null
		};
		a.key = So(a.elements), n.push(a), t.push([]);
	}), {
		segments: t,
		anchors: n
	};
}
function wo(e, t, n, r) {
	let i = [], a = () => {
		if (!i.length) return;
		let n = t[i[0].elementIndex], a = {
			...n,
			value: i.map((e) => e.char).join("")
		};
		r && (a.trace = [...n.trace || [], { type: r }]), e.push(a), i = [];
	};
	for (let e of n) i.length && e.elementIndex !== i[0].elementIndex && a(), i.push(e);
	a();
}
function To(e, t) {
	for (let n of e) {
		let e = n.trace || [];
		e[e.length - 1]?.type !== t && (n.trace = [...e, { type: t }]), n.control?.value && To(n.control.value, t), n.valueList && To(n.valueList, t);
		for (let e of n.trList || []) for (let n of e.tdList) To(n.value, t);
	}
}
function Eo(e, t) {
	let n = e || [], r = t || [], i = [], a = Math.min(n.length, r.length);
	for (let e = 0; e < a; e++) {
		let t = r[e], a = n[e].tdList, o = t.tdList, s = Math.min(a.length, o.length);
		for (let e = 0; e < s; e++) o[e].value = No(a[e].value, o[e].value);
		for (let e = s; e < a.length; e++) To(a[e].value, J.DELETED), t.tdList.push(a[e]);
		for (let e = s; e < o.length; e++) To(o[e].value, J.INSERTED);
		i.push(t);
	}
	for (let e = a; e < n.length; e++) {
		for (let t of n[e].tdList) To(t.value, J.DELETED);
		i.push(n[e]);
	}
	for (let e = a; e < r.length; e++) {
		for (let t of r[e].tdList) To(t.value, J.INSERTED);
		i.push(r[e]);
	}
	return i;
}
function Do(e, t) {
	let n = e.elements[0], r = t.elements[0];
	if (e.elements.length === 1 && t.elements.length === 1 && n.type === r.type) {
		if (r.type === H.CONTROL && r.control) return r.control = {
			...r.control,
			value: No(n.control?.value || [], r.control.value || [])
		}, [r];
		if (n.valueList || r.valueList) return r.valueList = No(n.valueList || [], r.valueList || []), [r];
		if (n.trList || r.trList) return r.trList = Eo(n.trList, r.trList), [r];
	}
	return t.elements;
}
function Oo(e) {
	let t = "", n = (e) => {
		for (let r of e) {
			t += r.value || "", r.control?.value && n(r.control.value), r.valueList && n(r.valueList);
			for (let e of r.trList || []) for (let t of e.tdList) n(t.value);
		}
	};
	return n(e.elements), t;
}
var ko = .5;
function Ao(e, t, n, r) {
	return e.key && t.key && e.key === t.key ? 2 : e.elements[0].type === t.elements[0].type ? !n && !r ? e.key && t.key ? 0 : 1 : +(vo(n, r) >= ko) : 0;
}
function jo(e, t) {
	let n = e.length, r = t.length, i = e.map(Oo), a = t.map(Oo), o = [], s = [];
	for (let e = 0; e <= n; e++) o.push(Array(r + 1).fill(0)), s.push(Array(r + 1).fill(0));
	for (let c = 1; c <= n; c++) for (let n = 1; n <= r; n++) {
		let r = Ao(e[c - 1], t[n - 1], i[c - 1], a[n - 1]);
		o[c][n] = r, s[c][n] = Math.max(s[c - 1][n], s[c][n - 1], r > 0 ? s[c - 1][n - 1] + r : 0);
	}
	let c = /* @__PURE__ */ new Map(), l = n, u = r;
	for (; l > 0 && u > 0;) {
		let e = o[l][u];
		e > 0 && s[l][u] === s[l - 1][u - 1] + e ? (c.set(u - 1, l - 1), l--, u--) : s[l][u] === s[l - 1][u] ? l-- : u--;
	}
	return c;
}
function Mo(e, t, n, r, i) {
	let a = xo(r.map((e) => e.char).join(""), i.map((e) => e.char).join("")), o = 0, s = 0;
	for (let c of a) {
		let a = [...c.value].length;
		c.type === "equal" ? (wo(e, n, i.slice(s, s + a)), o += a, s += a) : c.type === "insert" ? (wo(e, n, i.slice(s, s + a), J.INSERTED), s += a) : (wo(e, t, r.slice(o, o + a), J.DELETED), o += a);
	}
}
function No(e, t) {
	let n = Co(e), r = Co(t), i = jo(n.anchors, r.anchors), a = new Set(i.values()), o = [], s = 0, c = (t) => {
		wo(o, e, n.segments[t] || [], J.DELETED);
		let r = n.anchors[t];
		To(r.elements, J.DELETED), o.push(...r.elements);
	};
	for (let l = 0; l < r.anchors.length; l++) {
		let u = i.get(l);
		if (u === void 0) {
			wo(o, t, r.segments[l] || [], J.INSERTED);
			let e = r.anchors[l];
			To(e.elements, J.INSERTED), o.push(...e.elements);
			continue;
		}
		for (; s < u;) a.has(s) || c(s), s++;
		s = u + 1, Mo(o, e, t, n.segments[u] || [], r.segments[l] || []), o.push(...Do(n.anchors[u], r.anchors[l]));
	}
	for (; s < n.anchors.length;) a.has(s) || c(s), s++;
	return Mo(o, e, t, n.segments[n.anchors.length] || [], r.segments[r.anchors.length] || []), o;
}
function Po(e, t) {
	return No(k(e), k(t));
}
//#endregion
//#region src/editor/core/command/CommandAdapt.ts
var Fo = class {
	draw;
	range;
	position;
	historyManager;
	canvasEvent;
	options;
	control;
	workerManager;
	searchManager;
	i18n;
	zone;
	tableOperate;
	constructor(e) {
		this.draw = e, this.range = e.getRange(), this.position = e.getPosition(), this.historyManager = e.getHistoryManager(), this.canvasEvent = e.getCanvasEvent(), this.options = e.getOptions(), this.control = e.getControl(), this.workerManager = e.getWorkerManager(), this.searchManager = e.getSearch(), this.i18n = e.getI18n(), this.zone = e.getZone(), this.tableOperate = e.getTableOperate();
	}
	mode(e) {
		this.draw.setMode(e);
	}
	async cut() {
		this.draw.isReadonly() || this.draw.isDisabled() || await this.canvasEvent.cut();
	}
	async copy(e) {
		await this.canvasEvent.copy(e);
	}
	paste(e) {
		this.draw.isReadonly() || this.draw.isDisabled() || nr(this.canvasEvent, e);
	}
	selectAll() {
		this.canvasEvent.selectAll();
	}
	backspace() {
		if (this.draw.isReadonly()) return;
		let e = this.draw.getElementList(), { startIndex: t, endIndex: n } = this.range.getRange(), r = t === n;
		if (r && e[t].value === "​" && t === 0) return;
		r ? this.draw.deleteElementList(e, t, 1) : this.draw.deleteElementList(e, t + 1, n - t);
		let i = r ? t - 1 : t;
		this.range.setRange(i, i), this.draw.render({ curIndex: i });
	}
	setRange(e, t, n, r, i, a, o) {
		if (e < 0 || t < 0 || t < e) return;
		this.range.setRange(e, t, n, r, i, a, o);
		let s = e === t;
		this.draw.render({
			curIndex: s ? e : void 0,
			isCompute: !1,
			isSubmitHistory: !1,
			isSetCursor: s
		});
	}
	replaceRange(e) {
		this.setRange(e.startIndex, e.endIndex, e.tableId, e.startTdIndex, e.endTdIndex, e.startTrIndex, e.endTrIndex);
	}
	setPositionContext(e) {
		let { tableId: t, startTrIndex: n, startTdIndex: r } = e, i = this.draw.getOriginalElementList();
		if (t) {
			let e = i.findIndex((e) => e.id === t);
			if (!~e) return;
			let a = i[e].trList[n], o = a.tdList[r];
			this.position.setPositionContext({
				isTable: !0,
				index: e,
				trIndex: n,
				tdIndex: r,
				tdId: o.id,
				trId: a.id,
				tableId: t
			});
		} else this.position.setPositionContext({ isTable: !1 });
	}
	forceUpdate(e) {
		let { isSubmitHistory: t = !1 } = e || {};
		this.range.clearRange(), this.draw.render({
			isSubmitHistory: t,
			isSetCursor: !1
		});
	}
	blur() {
		this.range.clearRange(), this.draw.getCursor().recoveryCursor();
	}
	hideCursor() {
		this.draw.getCursor().recoveryCursor();
	}
	undo() {
		this.draw.isReadonly() || this.historyManager.undo();
	}
	redo() {
		this.draw.isReadonly() || this.historyManager.redo();
	}
	painter(e) {
		if (!e.isDblclick && this.draw.getPainterStyle()) {
			this.canvasEvent.clearPainterStyle();
			return;
		}
		let t = this.range.getSelection();
		if (!t) return;
		let n = {};
		t.forEach((e) => {
			[...Te, ...ke].forEach((t) => {
				let r = t;
				n[r] === void 0 && Reflect.set(n, r, e[r]);
			});
		}), this.draw.setPainterStyle(n, e);
	}
	applyPainterStyle() {
		this.draw.isReadonly() || this.draw.isDisabled() || this.canvasEvent.applyPainterStyle();
	}
	format(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let n = this.range.getSelectionElementList(), r = {}, i = [];
		if (n?.length) i = n, r = { isSetCursor: !1 };
		else {
			let { endIndex: e } = this.range.getRange();
			if (!~e) return;
			let t = this.draw.getElementList()[e];
			t?.value === "​" && (i.push(t), r = { curIndex: e });
		}
		i.length && (i.forEach((e) => {
			Te.forEach((t) => {
				delete e[t];
			});
		}), this.draw.render(r));
	}
	font(e, t) {
		let { isIgnoreDisabledRule: n = !1 } = t || {};
		if (!n && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let r = this.range.getSelectionElementList();
		if (r?.length) r.forEach((t) => {
			t.font = e;
		}), this.draw.render({ isSetCursor: !1 });
		else {
			let t = !0, { endIndex: n } = this.range.getRange();
			if (!~n) return;
			let r = this.draw.getElementList()[n];
			this.range.setDefaultStyle({ font: e }), r?.value === "​" ? r.font = e : t = !1, this.draw.render({
				isSubmitHistory: t,
				curIndex: n,
				isCompute: !1
			});
		}
	}
	size(e, t) {
		let { isIgnoreDisabledRule: n = !1 } = t || {};
		if (!n && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let { minSize: r, maxSize: i, defaultSize: a } = this.options;
		if (e < r || e > i) return;
		let o = {}, s = [], c = this.range.getTextLikeSelectionElementList();
		if (c?.length) s = c, o = { isSetCursor: !1 };
		else {
			let { endIndex: t } = this.range.getRange();
			if (!~t) return;
			let n = this.draw.getElementList()[t];
			this.range.setDefaultStyle({ size: e }), n?.value === "​" ? (s.push(n), o = { curIndex: t }) : this.draw.render({
				curIndex: t,
				isCompute: !1,
				isSubmitHistory: !1
			});
		}
		if (!s.length) return;
		let l = !1;
		s.forEach((t) => {
			!t.size && e === a || t.size && t.size === e || (t.size = e, l = !0);
		}), l && this.draw.render(o);
	}
	sizeAdd(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let { defaultSize: n, maxSize: r } = this.options, i = this.range.getTextLikeSelectionElementList(), a = {}, o = [];
		if (i?.length) o = i, a = { isSetCursor: !1 };
		else {
			let { endIndex: e } = this.range.getRange();
			if (!~e) return;
			let t = this.draw.getElementList()[e], i = this.range.getDefaultStyle()?.size || t.size || n;
			this.range.setDefaultStyle({ size: i + 2 > r ? r : i + 2 }), t?.value === "​" ? (o.push(t), a = { curIndex: e }) : this.draw.render({
				curIndex: e,
				isCompute: !1,
				isSubmitHistory: !1
			});
		}
		if (!o.length) return;
		let s = !1;
		o.forEach((e) => {
			e.size ||= n, !(e.size >= r) && (e.size + 2 > r ? e.size = r : e.size += 2, s = !0);
		}), s && this.draw.render(a);
	}
	sizeMinus(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let { defaultSize: n, minSize: r } = this.options, i = this.range.getTextLikeSelectionElementList(), a = {}, o = [];
		if (i?.length) o = i, a = { isSetCursor: !1 };
		else {
			let { endIndex: e } = this.range.getRange();
			if (!~e) return;
			let t = this.draw.getElementList()[e], i = this.range.getDefaultStyle()?.size || t.size || n;
			this.range.setDefaultStyle({ size: i - 2 < r ? r : i - 2 }), t?.value === "​" ? (o.push(t), a = { curIndex: e }) : this.draw.render({
				curIndex: e,
				isCompute: !1,
				isSubmitHistory: !1
			});
		}
		if (!o.length) return;
		let s = !1;
		o.forEach((e) => {
			e.size ||= n, !(e.size <= r) && (e.size - 2 < r ? e.size = r : e.size -= 2, s = !0);
		}), s && this.draw.render(a);
	}
	bold(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let n = this.range.getSelectionElementList();
		if (n?.length) {
			let e = n.findIndex((e) => !e.bold);
			n.forEach((t) => {
				t.bold = !!~e;
			}), this.draw.render({ isSetCursor: !1 });
		} else {
			let e = !0, { endIndex: t } = this.range.getRange();
			if (!~t) return;
			let n = this.draw.getElementList()[t];
			this.range.setDefaultStyle({ bold: !n.bold && !this.range.getDefaultStyle()?.bold }), n?.value === "​" ? n.bold = !n.bold : e = !1, this.draw.render({
				isSubmitHistory: e,
				curIndex: t,
				isCompute: !1
			});
		}
	}
	italic(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let n = this.range.getSelectionElementList();
		if (n?.length) {
			let e = n.findIndex((e) => !e.italic);
			n.forEach((t) => {
				t.italic = !!~e;
			}), this.draw.render({ isSetCursor: !1 });
		} else {
			let e = !0, { endIndex: t } = this.range.getRange();
			if (!~t) return;
			let n = this.draw.getElementList()[t];
			this.range.setDefaultStyle({ italic: !n.italic && !this.range.getDefaultStyle()?.italic }), n?.value === "​" ? n.italic = !n.italic : e = !1, this.draw.render({
				isSubmitHistory: e,
				curIndex: t,
				isCompute: !1
			});
		}
	}
	underline(e, t) {
		let { isIgnoreDisabledRule: n = !1 } = t || {};
		if (!n && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let r = this.range.getSelectionElementList();
		if (r?.length) {
			let t = r.some((t) => !t.underline || !e && t.textDecoration || e && !t.textDecoration || e && t.textDecoration && !le(t.textDecoration, e));
			r.forEach((n) => {
				n.underline = t, t && e ? n.textDecoration = e : delete n.textDecoration;
			}), this.draw.render({
				isSetCursor: !1,
				isCompute: !1
			});
		} else {
			let e = !0, { endIndex: t } = this.range.getRange();
			if (!~t) return;
			let n = this.draw.getElementList()[t];
			this.range.setDefaultStyle({ underline: !n?.underline && !this.range.getDefaultStyle()?.underline }), n?.value === "​" ? n.underline = !n.underline : e = !1, this.draw.render({
				isSubmitHistory: e,
				curIndex: t,
				isCompute: !1
			});
		}
	}
	strikeout(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let n = this.range.getSelectionElementList();
		if (n?.length) {
			let e = n.findIndex((e) => !e.strikeout);
			n.forEach((t) => {
				t.strikeout = !!~e;
			}), this.draw.render({
				isSetCursor: !1,
				isCompute: !1
			});
		} else {
			let e = !0, { endIndex: t } = this.range.getRange();
			if (!~t) return;
			let n = this.draw.getElementList()[t];
			this.range.setDefaultStyle({ strikeout: !n.strikeout && !this.range.getDefaultStyle()?.strikeout }), n?.value === "​" ? n.strikeout = !n.strikeout : e = !1, this.draw.render({
				isSubmitHistory: e,
				curIndex: t,
				isCompute: !1
			});
		}
	}
	superscript(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let n = this.range.getSelectionElementList();
		if (!n) return;
		let r = n.findIndex((e) => e.type === H.SUPERSCRIPT);
		n.forEach((e) => {
			~r ? e.type === H.SUPERSCRIPT && (e.type = H.TEXT, delete e.actualSize) : (!e.type || e.type === H.TEXT || e.type === H.SUBSCRIPT) && (e.type = H.SUPERSCRIPT);
		}), this.draw.render({ isSetCursor: !1 });
	}
	subscript(e) {
		let { isIgnoreDisabledRule: t = !1 } = e || {};
		if (!t && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let n = this.range.getSelectionElementList();
		if (!n) return;
		let r = n.findIndex((e) => e.type === H.SUBSCRIPT);
		n.forEach((e) => {
			~r ? e.type === H.SUBSCRIPT && (e.type = H.TEXT, delete e.actualSize) : (!e.type || e.type === H.TEXT || e.type === H.SUPERSCRIPT) && (e.type = H.SUBSCRIPT);
		}), this.draw.render({ isSetCursor: !1 });
	}
	color(e, t) {
		let { isIgnoreDisabledRule: n = !1 } = t || {};
		if (!n && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let r = this.range.getSelectionElementList();
		if (r?.length) r.forEach((t) => {
			e ? t.color = e : delete t.color;
		}), this.draw.render({
			isSetCursor: !1,
			isCompute: !1
		});
		else {
			let t = !0, { endIndex: n } = this.range.getRange();
			if (!~n) return;
			let r = this.draw.getElementList()[n];
			this.range.setDefaultStyle({ color: e || void 0 }), r?.value === "​" ? e ? r.color = e : delete r.color : t = !1, this.draw.render({
				isSubmitHistory: t,
				curIndex: n,
				isCompute: !1
			});
		}
	}
	highlight(e, t) {
		let { isIgnoreDisabledRule: n = !1 } = t || {};
		if (!n && (this.draw.isReadonly() || this.draw.isDisabled())) return;
		let r = this.range.getSelectionElementList();
		if (r?.length) r.forEach((t) => {
			e ? t.highlight = e : delete t.highlight;
		}), this.draw.render({
			isSetCursor: !1,
			isCompute: !1
		});
		else {
			let t = !0, { endIndex: n } = this.range.getRange();
			if (!~n) return;
			let r = this.draw.getElementList()[n];
			this.range.setDefaultStyle({ highlight: e || void 0 }), r?.value === "​" ? e ? r.highlight = e : delete r.highlight : t = !1, this.draw.render({
				isSubmitHistory: t,
				curIndex: n,
				isCompute: !1
			});
		}
	}
	title(e) {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return;
		let { startIndex: t, endIndex: n } = this.range.getRange();
		if (!~t && !~n) return;
		let r = this.draw.getElementList(), i = t === n ? this.range.getRangeParagraphElementList() : r.slice(t + 1, n + 1);
		if (!i || !i.length) return;
		let a = M(), o = this.draw.getOptions().title;
		i.forEach((t) => {
			!t.type && t.value === "​" || (e ? (t.level = e, t.titleId = a, Tn(t) && (t.size = o[Ct[e]], t.bold = !0)) : t.titleId && (delete t.titleId, delete t.title, delete t.level, delete t.size, delete t.bold));
		});
		let s = t === n, c = s ? n : t;
		this.draw.render({
			curIndex: c,
			isSetCursor: s
		});
	}
	list(e, t) {
		this.draw.isReadonly() || this.draw.getListParticle().setList(e, t);
	}
	rowFlex(e) {
		if (this.draw.isReadonly()) return;
		let { startIndex: t, endIndex: n } = this.range.getRange();
		if (!~t && !~n) return;
		let r = this.range.getRangeParagraphElementList();
		if (!r) return;
		r.forEach((t) => {
			t.rowFlex = e;
		});
		let i = t === n, a = i ? n : t;
		this.draw.render({
			curIndex: a,
			isSetCursor: i
		});
	}
	rowMargin(e) {
		if (this.draw.isReadonly()) return;
		let { startIndex: t, endIndex: n } = this.range.getRange();
		if (!~t && !~n) return;
		let r = this.range.getRangeParagraphElementList();
		if (!r) return;
		r.forEach((t) => {
			t.rowMargin = e;
		});
		let i = t === n, a = i ? n : t;
		this.draw.render({
			curIndex: a,
			isSetCursor: i
		});
	}
	insertTable(e, t) {
		this.draw.isReadonly() || this.draw.isDisabled() || this.control.getIsRangeWithinControl() || this.tableOperate.insertTable(e, t);
	}
	insertTableTopRow() {
		this.draw.isReadonly() || this.tableOperate.insertTableTopRow();
	}
	insertTableBottomRow() {
		this.draw.isReadonly() || this.tableOperate.insertTableBottomRow();
	}
	insertTableLeftCol() {
		this.draw.isReadonly() || this.tableOperate.insertTableLeftCol();
	}
	insertTableRightCol() {
		this.draw.isReadonly() || this.tableOperate.insertTableRightCol();
	}
	deleteTableRow() {
		this.draw.isReadonly() || this.tableOperate.deleteTableRow();
	}
	deleteTableCol() {
		this.draw.isReadonly() || this.tableOperate.deleteTableCol();
	}
	deleteTable() {
		this.draw.isReadonly() || this.tableOperate.deleteTable();
	}
	mergeTableCell() {
		this.draw.isReadonly() || this.tableOperate.mergeTableCell();
	}
	cancelMergeTableCell() {
		this.draw.isReadonly() || this.tableOperate.cancelMergeTableCell();
	}
	splitVerticalTableCell() {
		this.draw.isReadonly() || this.tableOperate.splitVerticalTableCell();
	}
	splitHorizontalTableCell() {
		this.draw.isReadonly() || this.tableOperate.splitHorizontalTableCell();
	}
	tableTdVerticalAlign(e) {
		this.draw.isReadonly() || this.tableOperate.tableTdVerticalAlign(e);
	}
	tableBorderType(e) {
		this.draw.isReadonly() || this.tableOperate.tableBorderType(e);
	}
	tableBorderColor(e) {
		this.draw.isReadonly() || this.tableOperate.tableBorderColor(e);
	}
	tableTdBorderType(e) {
		this.draw.isReadonly() || this.tableOperate.tableTdBorderType(e);
	}
	tableTdSlashType(e) {
		this.draw.isReadonly() || this.tableOperate.tableTdSlashType(e);
	}
	tableTdBackgroundColor(e) {
		this.draw.isReadonly() || this.tableOperate.tableTdBackgroundColor(e);
	}
	tableAutoFitToContent() {
		this.draw.isReadonly() || this.tableOperate.tableAutoFitToContent();
	}
	tableAutoFitToPage() {
		this.draw.isReadonly() || this.tableOperate.tableAutoFitToPage();
	}
	tableSelectAll() {
		this.tableOperate.tableSelectAll();
	}
	hyperlink(e) {
		let { valueList: t, url: n, hyperlinkId: r } = e;
		if (!n || !t?.length || this.draw.isReadonly() || this.draw.isDisabled() || this.control.getIsRangeWithinControl()) return;
		let { startIndex: i, endIndex: a } = this.range.getRange();
		!~i && !~a || this.insertElementList([{
			type: H.HYPERLINK,
			value: "",
			valueList: t,
			url: n,
			hyperlinkId: r || M()
		}]);
	}
	getHyperlinkRange() {
		let e = -1, t = -1, { startIndex: n, endIndex: r } = this.range.getRange();
		if (!~n && !~r) return null;
		let i = this.draw.getElementList(), a = i[n];
		if (a.type !== H.HYPERLINK) return null;
		let o = n;
		for (; o >= 0;) {
			if (i[o].hyperlinkId !== a.hyperlinkId) {
				e = o + 1;
				break;
			}
			o--;
		}
		let s = n + 1;
		for (; s <= i.length;) {
			if (i[s]?.hyperlinkId !== a.hyperlinkId) {
				t = s - 1;
				break;
			}
			s++;
		}
		return !~e || !~t ? null : [e, t];
	}
	deleteHyperlink() {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return;
		let e = this.getHyperlinkRange();
		if (!e) return;
		let t = this.draw.getElementList(), [n, r] = e;
		this.draw.deleteElementList(t, n, r - n + 1), this.draw.getHyperlinkParticle().clearHyperlinkPopup();
		let i = n - 1;
		this.range.setRange(i, i), this.draw.render({ curIndex: i });
	}
	cancelHyperlink() {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return;
		let e = this.getHyperlinkRange();
		if (!e) return;
		let t = this.draw.getElementList(), [n, r] = e;
		for (let e = n; e <= r; e++) {
			let n = t[e];
			delete n.type, delete n.url, delete n.hyperlinkId, delete n.underline;
		}
		this.draw.getHyperlinkParticle().clearHyperlinkPopup();
		let { endIndex: i } = this.range.getRange();
		this.draw.render({
			curIndex: i,
			isCompute: !1
		});
	}
	editHyperlink(e) {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return;
		let t = this.getHyperlinkRange();
		if (!t) return;
		let n = this.draw.getElementList(), [r, i] = t;
		for (let t = r; t <= i; t++) {
			let r = n[t];
			r.url = e;
		}
		this.draw.getHyperlinkParticle().clearHyperlinkPopup();
		let { endIndex: a } = this.range.getRange();
		this.draw.render({
			curIndex: a,
			isCompute: !1
		});
	}
	separator(e, t) {
		if (this.draw.isReadonly() || this.draw.isDisabled() || this.control.getIsRangeWithinControl()) return;
		let { startIndex: n, endIndex: r } = this.range.getRange();
		if (!~n && !~r) return;
		let i = this.draw.getElementList(), a = -1, o = i[r + 1];
		if (o && o.type === H.SEPARATOR) {
			if (o.dashArray && o.dashArray.join() === e.join()) return;
			let n = {
				...o,
				dashArray: e,
				...t
			};
			delete n.trace, this.draw.deleteElementList(i, r + 1, 1), this.draw.getTraceParticle().markElementListInserted([n]), this.draw.spliceElementList(i, r + 1, 0, [n]), a = r;
		} else {
			let r = {
				value: "\n",
				type: H.SEPARATOR,
				dashArray: e,
				...t
			};
			kn(i, [r], n, { editorOptions: this.options }), n !== 0 && i[n].value === "​" ? (this.draw.spliceElementList(i, n, 1, [r]), a = n - 1) : (this.draw.spliceElementList(i, n + 1, 0, [r]), a = n), this.draw.getTraceParticle().markElementListInserted([r]);
		}
		this.range.setRange(a, a), this.draw.render({ curIndex: a });
	}
	pageBreak() {
		this.draw.isReadonly() || this.draw.isDisabled() || this.control.getIsRangeWithinControl() || this.insertElementList([{
			type: H.PAGE_BREAK,
			value: "\n"
		}]);
	}
	addWatermark(e) {
		if (this.draw.isReadonly()) return;
		let t = this.draw.getOptions(), { color: n, size: r, opacity: i, font: a, gap: o, layer: s } = Qt;
		t.watermark.data = e.data, t.watermark.type = e.type || Xt.TEXT, e.width && (t.watermark.width = e.width), e.height && (t.watermark.height = e.height), t.watermark.color = e.color || n, t.watermark.opacity = e.opacity || i, t.watermark.size = e.size || r, t.watermark.font = e.font || a, t.watermark.repeat = !!e.repeat, e.numberType && (t.watermark.numberType = e.numberType), t.watermark.gap = e.gap || o, t.watermark.layer = e.layer || s, this.draw.render({
			isSetCursor: !1,
			isSubmitHistory: !1,
			isCompute: !1
		});
	}
	deleteWatermark() {
		if (this.draw.isReadonly()) return;
		let e = this.draw.getOptions();
		e.watermark && e.watermark.data && (e.watermark = { ...Qt }, this.draw.render({
			isSetCursor: !1,
			isSubmitHistory: !1,
			isCompute: !1
		}));
	}
	image(e) {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return null;
		let { startIndex: t, endIndex: n } = this.range.getRange();
		if (!~t && !~n) return null;
		let r = e.id || M();
		return this.insertElementList([{
			...e,
			id: r,
			type: H.IMAGE
		}]), r;
	}
	search(e, t) {
		this.searchManager.setSearchKeyword(e, t), this.draw.render({ isSubmitHistory: !1 });
	}
	setSpellcheckRangeList(e) {
		if (!this.draw.getSpellcheck().setSpellcheckRangeList(e)) return;
		let t = this.position.getCursorPosition(), n = this.range.getIsCollapsed();
		this.draw.render({
			isCompute: !1,
			isSubmitHistory: !1,
			isSetCursor: n && !!t,
			curIndex: t?.index
		});
	}
	getSpellcheckWordList() {
		return this.draw.getSpellcheck().getSpellcheckWordList();
	}
	searchNavigatePre() {
		this.searchManager.searchNavigatePre() !== null && this.draw.render({
			isSetCursor: !1,
			isSubmitHistory: !1,
			isCompute: !1,
			isLazy: !1
		});
	}
	searchNavigateNext() {
		this.searchManager.searchNavigateNext() !== null && this.draw.render({
			isSetCursor: !1,
			isSubmitHistory: !1,
			isCompute: !1,
			isLazy: !1
		});
	}
	getSearchNavigateInfo() {
		return this.searchManager.getSearchNavigateInfo();
	}
	replace(e, t) {
		this.draw.getSearch().replace(e, t);
	}
	async print(e) {
		if (e?.offscreen) {
			let t = e.data ?? this.draw.getValue().data, n = e.options ?? this.draw.getOptions(), r = document.createElement("div");
			r.style.position = "absolute", r.style.left = "-9999px", r.style.top = "0", r.style.visibility = "hidden", document.body.append(r);
			let { default: i } = await import("./canvas-editor.js"), a = null;
			try {
				a = new i(r, t, n), await a.command.executePrint();
			} finally {
				a?.destroy(), r.remove();
			}
			return;
		}
		let { scale: t, printPixelRatio: n, paperDirection: r, width: i, height: a } = this.options;
		t !== 1 && this.draw.setPageScale(1), await uo(await this.draw.getDataURL({
			pixelRatio: n,
			mode: p.PRINT
		}), {
			width: i,
			height: a,
			direction: r,
			pageDirections: this.draw.getPageDirectionList(),
			iframeInfoList: this.draw.getBlockParticle().pickIframeInfo()
		}), t !== 1 && this.draw.setPageScale(t);
	}
	replaceImageElement(e) {
		let { startIndex: t } = this.range.getRange(), n = this.draw.getElementList()[t];
		!n || n.type !== H.IMAGE || (n.value = e, this.draw.render({ isSetCursor: !1 }));
	}
	saveAsImageElement() {
		let { startIndex: e } = this.range.getRange(), t = this.draw.getElementList()[e];
		!t || t.type !== H.IMAGE || ee(t.value, `${t.id}.png`);
	}
	setImageCrop(e) {
		let { startIndex: t } = this.range.getRange(), n = this.draw.getElementList()[t];
		!n || n.type !== H.IMAGE || (n.imgCrop = e, this.draw.render({
			isSetCursor: !1,
			isCompute: !1
		}));
	}
	setImageCaption(e) {
		let { startIndex: t } = this.range.getRange(), n = this.draw.getElementList()[t];
		n?.type === H.IMAGE && (n.imgCaption = e, this.draw.render({ isSetCursor: !1 }));
	}
	changeImageDisplay(e, t) {
		if (e.imgDisplay === t) return;
		e.imgDisplay = t;
		let { startIndex: n, endIndex: i } = this.range.getRange();
		if (t === r.SURROUND || t === r.FLOAT_TOP || t === r.FLOAT_BOTTOM) {
			let t = this.position.getPositionList(), r = this.position.getPositionContext(), { pageNo: i, coordinate: { leftTop: a } } = t[n], o = (r.isTable ? this.position.getOriginalPositionList()[r.index] : null)?.coordinate.leftTop;
			e.imgFloatPosition = {
				pageNo: i,
				x: o ? a[0] - o[0] : a[0],
				y: o ? a[1] - o[1] : a[1]
			};
		} else delete e.imgFloatPosition;
		this.draw.getPreviewer().clearResizer(), this.draw.render({
			isSetCursor: !0,
			curIndex: i
		});
	}
	getImage(e) {
		return this.draw.getDataURL(e);
	}
	getOptions() {
		return this.options;
	}
	getValue(e) {
		return this.draw.getValue(e);
	}
	getValueAsync(e) {
		return this.draw.getWorkerManager().getValue(e);
	}
	getAreaValue(e) {
		return this.draw.getArea().getAreaValue(e);
	}
	getHTML() {
		let e = this.options, t = this.draw.getHeaderElementList(), n = this.draw.getOriginalMainElementList(), r = this.draw.getFooterElementList();
		return {
			header: Nn(gn(t), e).innerHTML,
			main: Nn(gn(n), e).innerHTML,
			footer: Nn(gn(r), e).innerHTML
		};
	}
	getText() {
		let e = this.draw.getHeaderElementList(), t = this.draw.getOriginalMainElementList(), n = this.draw.getFooterElementList();
		return {
			header: In(gn(e), { isClone: !1 }),
			main: In(gn(t), { isClone: !1 }),
			footer: In(gn(n), { isClone: !1 })
		};
	}
	getWordCount() {
		return this.workerManager.getWordCount();
	}
	getCursorPosition() {
		return this.position.getCursorPosition();
	}
	getRemainingContentHeight() {
		if (!this.draw.getIsPagingMode()) return 0;
		let e = this.draw.getPageRowList(), t = e.length - 1, n = (e[t] || []).reduce((e, t) => e + t.height + (t.offsetY || 0), 0), r = this.draw.getHeight() - (this.draw.getMainOuterHeight(t) + n);
		return r > 0 ? r : 0;
	}
	computeElementListHeight(e) {
		if (!e.length) return 0;
		let t = this.draw.getInnerWidth();
		if (t <= 0) return 0;
		let n = k(e);
		yn(n, {
			isHandleFirstElement: !1,
			editorOptions: this.options
		});
		let r = Bn(n);
		return this.draw.computeRowList({
			innerWidth: t,
			elementList: n,
			surroundElementList: r
		}).reduce((e, t) => e + t.height + (t.offsetY || 0), 0);
	}
	getRange() {
		return k(this.range.getRange());
	}
	getRangeText() {
		return this.range.toString();
	}
	getRangeContext() {
		let { startIndex: e, endIndex: t } = this.range.getRange();
		if (!~e && !~t) return null;
		let n = e === t, r = this.range.toString(), i = X(gn(this.range.getSelectionElementList() || []), { isClone: !1 }), a = this.draw.getElementList(), o = xn(a[n ? e : e + 1], { extraPickAttrs: ["id", "controlComponent"] }), s = xn(a[t], { extraPickAttrs: ["id", "controlComponent"] }), c = this.draw.getRowList(), l = this.position.getPositionList(), u = l[e], d = l[t], f = u.pageNo, p = d.pageNo, m = u.rowIndex, h = d.rowIndex, g = c[m], _ = c[h], v = 0, y = 0;
		this.draw.getCursor().getHitLineStartIndex() || (v = g.elementList[0]?.value === "​" ? u.index - g.startIndex : u.index - g.startIndex + 1), y = u === d ? v : _.elementList[0]?.value === "​" ? d.index - _.startIndex : d.index - _.startIndex + 1;
		let b = [], x = this.position.getSelectionPositionList();
		if (x) {
			let e = null, t = 0, n = null;
			for (let r = 0; r < x.length; r++) {
				let { rowNo: i, pageNo: a, coordinate: { leftTop: o, rightTop: s }, lineHeight: c } = x[r], l = this.draw.getPageOffset(a, !0);
				e === null || e !== i ? (n && b.push(n), n = {
					x: o[0] + l.x,
					y: o[1] + l.y,
					width: s[0] - o[0],
					height: c
				}, e = i, t = o[0]) : n.width = s[0] - t, r === x.length - 1 && n && b.push(n);
			}
		} else {
			let { coordinate: { rightTop: e }, pageNo: n, lineHeight: r } = this.position.getPositionList()[t], i = this.draw.getPageOffset(n, !0);
			b.push({
				x: e[0] + i.x,
				y: e[1] + i.y,
				width: 0,
				height: r
			});
		}
		let S = this.draw.getZone().getZone(), { isTable: C, trIndex: w, tdIndex: T, index: E } = this.position.getPositionContext(), D = null;
		if (C) {
			let e = this.draw.getOriginalElementList()[E] || null;
			e && (D = X([e])[0]);
		}
		let O = null, A = null, j = e - 1;
		for (; j > 0;) {
			let e = a[j], t = a[j - 1];
			if (e.titleId && e.titleId !== t?.titleId) {
				O = e.titleId, A = l[j].pageNo;
				break;
			}
			j--;
		}
		let M = co(a, e), N = e === t ? M : co(a, t);
		return k({
			isCollapsed: n,
			startElement: o,
			endElement: s,
			startPageNo: f,
			endPageNo: p,
			startRowNo: m,
			endRowNo: h,
			startColNo: v,
			endColNo: y,
			rangeRects: b,
			zone: S,
			isTable: C,
			trIndex: w ?? null,
			tdIndex: T ?? null,
			tableElement: D,
			selectionText: r,
			selectionElementList: i,
			titleId: O,
			titleStartPageNo: A,
			startParagraphNo: M,
			endParagraphNo: N
		});
	}
	getRangeRow() {
		let e = this.range.getRangeRowElementList();
		return e ? X(gn(e), { isClone: !1 }) : null;
	}
	getRangeParagraph() {
		let e = this.range.getRangeParagraphElementList();
		return e ? X(gn(e), { isClone: !1 }) : null;
	}
	getKeywordRangeList(e) {
		return this.range.getKeywordRangeList(e);
	}
	getKeywordContext(e) {
		let t = this.getKeywordRangeList(e);
		if (!t.length) return null;
		let n = [], r = this.position.getOriginalMainPositionList(), i = this.draw.getOriginalMainElementList();
		for (let e = 0; e < t.length; e++) {
			let a = t[e], { startIndex: o, endIndex: s, tableId: c, startTrIndex: l, startTdIndex: u } = a, d = r;
			if (a.tableId) {
				let e = i.find((e) => e.id === c);
				e && (d = e.trList?.[l]?.tdList?.[u]?.positionList || []);
			}
			let f = k(d[o]), p = k(d[s]);
			n.push({
				range: a,
				startPosition: f,
				endPosition: p
			});
		}
		return n;
	}
	pageMode(e) {
		this.draw.setPageMode(e);
	}
	setColumns(e) {
		this.draw.setColumnConfig(e), this.draw.render({
			isSubmitHistory: !1,
			isSetCursor: !1
		});
	}
	getColumns() {
		let e = this.draw.getColumnLayout();
		return e ? {
			count: e.count,
			gap: e.gap,
			separator: e.separator
		} : null;
	}
	pageScale(e) {
		e !== this.options.scale && this.draw.setPageScale(e);
	}
	pageScaleRecovery() {
		let { scale: e } = this.options;
		e !== 1 && this.draw.setPageScale(1);
	}
	pageScaleMinus() {
		let { scale: e } = this.options, t = e * 10 - 1;
		t >= 5 && this.draw.setPageScale(t / 10);
	}
	pageScaleAdd() {
		let { scale: e } = this.options, t = e * 10 + 1;
		t <= 30 && this.draw.setPageScale(t / 10);
	}
	paperSize(e, t) {
		this.draw.setPaperSize(e, t);
	}
	paperDirection(e) {
		this.draw.setPaperDirection(e);
	}
	pageDirection(e) {
		this.draw.setPageDirection(e);
	}
	getPaperMargin() {
		return this.options.margins;
	}
	setPaperMargin(e) {
		return this.draw.setPaperMargin(e);
	}
	setMainBadge(e) {
		this.draw.getBadge().setMainBadge(e), this.draw.render({
			isCompute: !1,
			isSubmitHistory: !1
		});
	}
	setAreaBadge(e) {
		this.draw.getBadge().setAreaBadgeMap(e), this.draw.render({
			isCompute: !1,
			isSubmitHistory: !1
		});
	}
	insertElementList(e, t = {}) {
		if (!e.length || this.draw.isReadonly() || this.draw.isDisabled()) return;
		let { isReplace: n = !0, ignoreContextKeys: r } = t;
		n || this.range.shrinkRange();
		let i = k(e), { startIndex: a } = this.range.getRange();
		kn(this.draw.getElementList(), i, a, {
			ignoreContextKeys: r,
			isBreakWhenWrap: !0,
			editorOptions: this.options
		}), this.draw.insertElementList(i, t);
	}
	appendElementList(e, t) {
		if (!e.length || this.draw.isReadonly()) return;
		let n = k(e);
		this.draw.appendElementList(n, t);
	}
	updateElementById(e) {
		let { id: t, conceptId: n } = e;
		if (!t && !n) return;
		let r = [];
		function i(e) {
			let a = 0;
			for (; a < e.length;) {
				let o = e[a];
				if (a++, !hn(o)) {
					if (o.type === H.TABLE) {
						let e = o.trList;
						for (let t = 0; t < e.length; t++) {
							let n = e[t];
							for (let e = 0; e < n.tdList.length; e++) {
								let t = n.tdList[e];
								i(t.value);
							}
						}
					}
					(t && o.id === t || n && o.conceptId === n) && r.push({
						elementList: e,
						index: a - 1
					});
				}
			}
		}
		let a = [
			this.draw.getOriginalMainElementList(),
			this.draw.getHeaderElementList(),
			this.draw.getFooterElementList()
		];
		for (let e of a) i(e);
		if (r.length) {
			for (let t = 0; t < r.length; t++) {
				let { elementList: n, index: i } = r[t], a = n[i];
				if (a.type === H.BLOCK || a.type === H.IMAGE || a.type === H.LATEX) n[i] = {
					...a,
					...e.properties,
					type: a.type
				};
				else {
					let t = X([{
						...a,
						...e.properties
					}], { extraPickAttrs: ["id"] });
					B(Re, a, t[0]), yn(t, {
						isHandleFirstElement: !1,
						editorOptions: this.options
					}), n[i] = t[0];
				}
			}
			this.draw.render({ isSetCursor: !1 });
		}
	}
	deleteElementById(e) {
		let { id: t, conceptId: n } = e;
		if (!t && !n) return;
		let r = !1, i = (e) => {
			let a = 0;
			for (; a < e.length;) {
				let o = e[a];
				if (o.type === H.TABLE) {
					let e = o.trList;
					for (let t = 0; t < e.length; t++) {
						let n = e[t];
						for (let e = 0; e < n.tdList.length; e++) {
							let t = n.tdList[e];
							i(t.value);
						}
					}
				}
				(t && o.id === t || n && o.conceptId === n) && (r = !0, this.draw.deleteElementList(e, a, 1, { isIgnoreDeletedRule: !0 })), a++;
			}
		}, a = [
			this.draw.getOriginalMainElementList(),
			this.draw.getHeaderElementList(),
			this.draw.getFooterElementList()
		];
		for (let e of a) i(e);
		r && this.draw.render({ isSetCursor: !1 });
	}
	getElementById(e) {
		let { id: t, conceptId: n } = e, r = [];
		if (!t && !n) return r;
		let i = (e) => {
			let a = 0;
			for (; a < e.length;) {
				let o = e[a];
				if (a++, !hn(o)) {
					if (o.type === H.TABLE) {
						let e = o.trList;
						for (let t = 0; t < e.length; t++) {
							let n = e[t];
							for (let e = 0; e < n.tdList.length; e++) {
								let t = n.tdList[e];
								i(t.value);
							}
						}
					}
					t && o.id !== t || n && o.conceptId !== n || r.push(o);
				}
			}
		}, a = [
			this.draw.getHeaderElementList(),
			this.draw.getOriginalMainElementList(),
			this.draw.getFooterElementList()
		];
		for (let e of a) i(e);
		return X(r, { extraPickAttrs: ["id"] });
	}
	setValue(e, t) {
		this.draw.setValue(e, t);
	}
	removeControl(e) {
		if (e?.id || e?.conceptId) {
			let { id: t, conceptId: n } = e, r = !1, i = (e) => {
				let a = e.length - 1;
				for (; a >= 0;) {
					let o = e[a];
					if (o.type === H.TABLE) {
						let e = o.trList;
						for (let t = 0; t < e.length; t++) {
							let n = e[t];
							for (let e = 0; e < n.tdList.length; e++) {
								let t = n.tdList[e];
								i(t.value);
							}
						}
					}
					a--, !(!o.control || t && o.controlId !== t || n && o.control.conceptId !== n) && (r = !0, this.draw.deleteElementList(e, a + 1, 1, { isIgnoreDeletedRule: !0 }));
				}
			}, a = [
				this.draw.getHeaderElementList(),
				this.draw.getOriginalMainElementList(),
				this.draw.getFooterElementList()
			];
			for (let e of a) i(e);
			r && this.draw.render({ isSetCursor: !1 });
		} else {
			let { startIndex: e, endIndex: t } = this.range.getRange();
			if (e !== t || !this.draw.getElementList()[e].controlId) return;
			let n = this.draw.getControl().removeControl(e);
			if (n === null) return;
			this.range.setRange(n, n), this.draw.render({ curIndex: n });
		}
	}
	translate(e) {
		return this.i18n.t(e);
	}
	setLocale(e) {
		this.i18n.setLocale(e);
	}
	getLocale() {
		return this.i18n.getLocale();
	}
	getCatalog() {
		return this.workerManager.getCatalog();
	}
	locationCatalog(e) {
		let t = this.draw.getOriginalElementList();
		function n(e, t) {
			for (let r = 0; r < e.length; r++) {
				let i = e[r];
				if (i.type === H.TABLE) {
					let e = i.trList;
					for (let a = 0; a < e.length; a++) {
						let o = e[a];
						for (let e = 0; e < o.tdList.length; e++) {
							let s = o.tdList[e], c = n(s.value, t);
							if (c) return {
								...c,
								isTable: !0,
								index: r,
								trIndex: a,
								tdIndex: e,
								tdId: s.id,
								trId: o.id,
								tableId: i.id
							};
						}
					}
				}
				if (i.titleId === t) {
					let n = r;
					for (; n < e.length;) {
						if (e[n + 1]?.titleId !== t) return {
							isTable: !1,
							startIndex: n,
							endIndex: n
						};
						n++;
					}
				}
			}
			return null;
		}
		let r = n(t, e);
		if (!r) return;
		let { isTable: i, index: a, startTdIndex: o, endTdIndex: s, startTrIndex: c, endTrIndex: l, trIndex: u, tdIndex: d, tdId: f, trId: p, tableId: m, endIndex: h } = r;
		this.position.setPositionContext({
			isTable: i,
			index: a,
			trIndex: u,
			tdIndex: d,
			tdId: f,
			trId: p,
			tableId: m
		}), this.range.setRange(h, h, m, o, s, c, l), this.draw.render({
			curIndex: h,
			isCompute: !1,
			isSubmitHistory: !1
		});
	}
	wordTool() {
		let e = this.draw.getMainElementList(), t = !1;
		for (let n = 0; n < e.length; n++) if (e[n].value === "​") for (; n + 1 < e.length;) {
			let r = e[n + 1];
			if (r.value !== "​" && r.value !== " ") break;
			e.splice(n + 1, 1), t = !0;
		}
		if (t) this.draw.render({ isSetCursor: !1 });
		else {
			let e = this.range.getIsCollapsed();
			this.draw.getCursor().drawCursor({ isShow: e });
		}
	}
	setHTML(e) {
		let { header: t, main: n, footer: r } = e, i = this.draw.getOriginalInnerWidth(), a = (e) => e === void 0 ? void 0 : Fn(e, { innerWidth: i });
		this.setValue({
			header: a(t),
			main: a(n),
			footer: a(r)
		});
	}
	setGroup() {
		return this.draw.getGroup().setGroup();
	}
	deleteGroup(e) {
		this.draw.getGroup().deleteGroup(e);
	}
	getGroupIds() {
		return this.draw.getWorkerManager().getGroupIds();
	}
	getGroupRectList(e) {
		let t = this.draw.getOriginalMainElementList(), n = this.draw.getGroup().getContextByGroupId(t, e);
		if (!n) return null;
		let { isTable: r, index: i, trIndex: a, tdIndex: o, endIndex: s } = n, c = r ? t[i].trList[a].tdList[o].value : t, l = s;
		for (; l > 0 && c[l - 1]?.groupIds?.includes(e);) l--;
		let u = (r ? this.position.getTableTdByContext(t, n)?.positionList || [] : this.position.getOriginalMainPositionList()).slice(l, s + 1);
		if (!u.length) return null;
		let d = [], f = null, p = null, m = 0, h = null;
		for (let e = 0; e < u.length; e++) {
			let { rowNo: t, pageNo: n, coordinate: { leftTop: r, rightTop: i }, lineHeight: a } = u[e];
			if (f !== t || p !== n) {
				h && d.push(h);
				let e = this.draw.getPageOffset(n, !0);
				h = {
					x: r[0] + e.x,
					y: r[1] + e.y,
					width: i[0] - r[0],
					height: a
				}, f = t, p = n, m = r[0];
			} else h.width = i[0] - m;
		}
		return h && d.push(h), d;
	}
	locationGroup(e) {
		let t = this.draw.getOriginalMainElementList(), n = this.draw.getGroup().getContextByGroupId(t, e);
		if (!n) return;
		let { isTable: r, index: i, trIndex: a, tdIndex: o, tdId: s, trId: c, tableId: l, endIndex: u } = n;
		this.position.setPositionContext({
			isTable: r,
			index: i,
			trIndex: a,
			tdIndex: o,
			tdId: s,
			trId: c,
			tableId: l
		}), this.range.setRange(u, u), this.draw.render({
			curIndex: u,
			isCompute: !1,
			isSubmitHistory: !1
		});
	}
	setZone(e) {
		this.draw.getZone().setZone(e);
	}
	getControlValue(e) {
		return this.draw.getControl().getValueById(e);
	}
	setControlValue(e) {
		this.draw.getControl().setValueListById([e]);
	}
	setControlValueList(e) {
		this.draw.getControl().setValueListById(e);
	}
	setControlExtension(e) {
		this.draw.getControl().setExtensionListById([e]);
	}
	setControlExtensionList(e) {
		this.draw.getControl().setExtensionListById(e);
	}
	setControlProperties(e) {
		this.draw.getControl().setPropertiesListById([e]);
	}
	setControlPropertiesList(e) {
		this.draw.getControl().setPropertiesListById(e);
	}
	validate(e) {
		return this.draw.getValidate().execute(e);
	}
	clearValidate() {
		this.draw.getValidate().clearHighlight();
	}
	setControlHighlight(e) {
		this.draw.getControl().setHighlightList(e), this.draw.render({ isSubmitHistory: !1 });
	}
	updateOptions(e) {
		let t = mn(e);
		Object.entries(t).forEach(([e, t]) => {
			Reflect.set(this.options, e, t);
		}), this.forceUpdate();
	}
	getControlList() {
		return this.draw.getControl().getList();
	}
	locationControl(e, t) {
		function n(r, a) {
			let o = 0;
			for (; o < r.length;) {
				let s = r[o];
				if (o++, s.type === H.TABLE) {
					let e = s.trList;
					for (let t = 0; t < e.length; t++) {
						let r = e[t];
						for (let e = 0; e < r.tdList.length; e++) {
							let i = r.tdList[e], c = n(i.value, a);
							if (c) return {
								...c,
								positionContext: {
									isTable: !0,
									index: o - 1,
									trIndex: t,
									tdIndex: e,
									tdId: s.tdId,
									trId: s.trId,
									tableId: s.tableId
								}
							};
						}
					}
				}
				if (s?.controlId !== e) continue;
				let c = o - 1;
				if (t?.position === i.OUTER_AFTER) {
					if (s.controlComponent !== K.POSTFIX || r[o + 1]?.controlComponent === K.POST_TEXT) continue;
				} else if (t?.position === i.OUTER_BEFORE) --c;
				else if (t?.position === i.AFTER) {
					if (--c, s.controlComponent !== K.PLACEHOLDER && s.controlComponent !== K.POSTFIX && s.controlComponent !== K.POST_TEXT) continue;
				} else if (s.controlComponent !== K.PREFIX && s.controlComponent !== K.PRE_TEXT || r[o]?.controlComponent === K.PREFIX || r[o]?.controlComponent === K.PRE_TEXT) continue;
				return {
					zone: a,
					range: {
						startIndex: c,
						endIndex: c
					},
					positionContext: { isTable: !1 }
				};
			}
			return null;
		}
		let r = [
			{
				zone: m.HEADER,
				elementList: this.draw.getHeaderElementList()
			},
			{
				zone: m.MAIN,
				elementList: this.draw.getOriginalMainElementList()
			},
			{
				zone: m.FOOTER,
				elementList: this.draw.getFooterElementList()
			}
		];
		for (let e of r) {
			let t = n(e.elementList, e.zone);
			if (t) {
				this.setZone(t.zone), this.position.setPositionContext(t.positionContext), this.range.replaceRange(t.range), this.draw.render({
					curIndex: t.range.startIndex,
					isCompute: !1,
					isSubmitHistory: !1
				});
				break;
			}
		}
	}
	insertControl(e) {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return;
		let t = k(e), { startIndex: n } = this.range.getRange(), r = this.draw.getElementList(), i = r[n];
		if (i?.controlId && i.control?.type !== G.TEXT && t.type === H.CONTROL && r[n + 1]?.controlId === i.controlId) return;
		let a = On(r, n);
		a && (B([
			...Ne,
			...Ee,
			...Fe,
			...Re
		], a, t), this.draw.insertElementList([t]));
	}
	jumpControl(e) {
		this.draw.getControl().initNextControl({ direction: e?.direction });
	}
	getContainer() {
		return this.draw.getContainer();
	}
	getTitleValue(e) {
		let { conceptId: t } = e, n = [], r = (e, i) => {
			let a = 0;
			for (; a < e.length;) {
				let o = e[a];
				if (a++, o.type === H.TABLE) {
					let e = o.trList;
					for (let t = 0; t < e.length; t++) {
						let n = e[t];
						for (let e = 0; e < n.tdList.length; e++) {
							let t = n.tdList[e];
							r(t.value, i);
						}
					}
				}
				if (hn(o) || o?.title?.conceptId !== t) continue;
				let s = [], c = a;
				for (; c < e.length;) {
					let t = e[c];
					if (c++, o.titleId !== t.titleId) {
						if (t.level && wt[t.level] <= wt[o.level]) break;
						s.push(t);
					}
				}
				let l = gn(s);
				n.push({
					...o.title,
					value: In(l),
					elementList: X(l, { isClone: !1 }),
					zone: i
				}), a = c;
			}
		}, i = [
			{
				zone: m.HEADER,
				elementList: this.draw.getHeaderElementList()
			},
			{
				zone: m.MAIN,
				elementList: this.draw.getOriginalMainElementList()
			},
			{
				zone: m.FOOTER,
				elementList: this.draw.getFooterElementList()
			}
		];
		for (let { zone: e, elementList: t } of i) r(t, e);
		return n;
	}
	getPositionContextByEvent(e, t = {}) {
		let n = e.target?.dataset.index;
		if (!n) return null;
		let { isMustDirectHit: r = !0 } = t, i = Number(n), { isDirectHit: a, isTable: o, index: s, trIndex: c, tdIndex: l, tdValueIndex: u, zone: d } = this.position.getPositionByXY({
			x: e.offsetX,
			y: e.offsetY,
			pageNo: i
		});
		if (r && !a || d && d !== this.zone.getZone()) return null;
		let f = null, p = null, m = this.draw.getOriginalElementList(), h = null, g = this.position.getOriginalPositionList();
		if (o) {
			let e = m[s].trList?.[c].tdList[l];
			p = e?.value[u] || null, h = e?.positionList?.[u] || null, f = {
				element: m[s],
				trIndex: c,
				tdIndex: l
			};
		} else p = m[s] || null, h = g[s] || null;
		let _ = null;
		if (h) {
			let { pageNo: e, coordinate: { leftTop: t, rightTop: n }, lineHeight: r } = h, i = this.draw.getPageOffset(e, !0);
			_ = {
				x: t[0] + i.x,
				y: t[1] + i.y,
				width: n[0] - t[0],
				height: r
			};
		}
		return {
			pageNo: i,
			element: p,
			rangeRect: _,
			tableInfo: f
		};
	}
	insertTitle(e) {
		if (this.draw.isReadonly() || this.draw.isDisabled()) return;
		let t = k(e), { startIndex: n } = this.range.getRange(), r = On(this.draw.getElementList(), n);
		if (!r) return;
		let i = [
			...Ne,
			...Ee,
			...Fe,
			...Re
		];
		t.valueList?.forEach((e) => {
			B(i, r, e);
		}), this.draw.insertElementList([t]);
	}
	focus(e) {
		let { position: t = i.AFTER, isMoveCursorToVisible: n = !0, rowNo: r, range: a } = e || {}, o = -1;
		if (a) this.range.replaceRange(a), o = t === i.BEFORE ? a.startIndex : a.endIndex;
		else if (L(r)) {
			let e = this.draw.getOriginalRowList();
			if (o = t === i.BEFORE ? e[r]?.startIndex : e[r + 1]?.startIndex - 1, !L(o)) return;
			this.range.setRange(o, o);
		} else o = t === i.BEFORE ? 0 : this.draw.getOriginalMainElementList().length - 1, this.range.setRange(o, o);
		let s = {
			isCompute: !1,
			isSetCursor: !1,
			isSubmitHistory: !1
		};
		n && ~o && this.range.getIsCollapsed() && (s.curIndex = o, s.isSetCursor = !0), this.draw.render(s);
	}
	insertArea(e) {
		return this.draw.getArea().insertArea(e);
	}
	setAreaValue(e) {
		return this.draw.getArea().setAreaValue(e);
	}
	setAreaProperties(e) {
		this.draw.getArea().setAreaProperties(e);
	}
	deleteArea(e) {
		this.draw.getArea().deleteArea(e);
	}
	locationArea(e, t) {
		if (t?.isAppendLastLineBreak && t?.position === i.OUTER_AFTER) {
			let t = this.draw.getOriginalMainElementList();
			t[t.length - 1].areaId === e && this.draw.appendElementList([{ value: "​" }], { isSubmitHistory: !1 });
		}
		let n = this.draw.getArea().getContextByAreaId(e, t);
		if (!n) return;
		let { range: { endIndex: r } } = n;
		this.position.setPositionContext({ isTable: !1 }), this.range.setRange(r, r), this.draw.render({
			curIndex: r,
			isSetCursor: !0,
			isCompute: !1,
			isSubmitHistory: !1
		});
	}
	clearGraffiti() {
		this.draw.getGraffiti().clear(), this.draw.isGraffitiMode() && this.draw.render({
			isCompute: !1,
			isSetCursor: !1,
			isSubmitHistory: !1
		});
	}
	toggleTrace(e) {
		let t = e === void 0 ? this.draw.getOptions().trace.disabled : e;
		this.draw.setTraceEnabled(t);
	}
	compare(e) {
		let t = e.newData ?? _n(this.getValue().data.main), n = Po(e.oldData, t);
		this.draw.setValue({ main: n }), this.draw.setMode(p.TRACE);
	}
	toggleRuler(e) {
		let t = e === void 0 ? this.draw.getOptions().ruler.disabled : e;
		this.draw.setRulerEnabled(t);
	}
}, Io = class {
	rangeStyleChange;
	visiblePageNoListChange;
	intersectionPageNoChange;
	pageSizeChange;
	pageScaleChange;
	saved;
	contentChange;
	controlChange;
	controlContentChange;
	pageModeChange;
	zoneChange;
	constructor() {
		this.rangeStyleChange = null, this.visiblePageNoListChange = null, this.intersectionPageNoChange = null, this.pageSizeChange = null, this.pageScaleChange = null, this.saved = null, this.contentChange = null, this.controlChange = null, this.controlContentChange = null, this.pageModeChange = null, this.zoneChange = null;
	}
}, Lo = class {
	contextMenuList;
	getContextMenuList;
	shortcutList;
	langMap;
	constructor(e) {
		let { contextMenu: t, shortcut: n, i18n: r } = e;
		this.contextMenuList = t.registerContextMenuList.bind(t), this.getContextMenuList = t.getContextMenuList.bind(t), this.shortcutList = n.registerShortcutList.bind(n), this.langMap = r.registerLangMap.bind(r);
	}
}, Ro = { SELECTED_TEXT: "%s" }, zo = {
	GLOBAL: {
		CUT: "globalCut",
		COPY: "globalCopy",
		PASTE: "globalPaste",
		SELECT_ALL: "globalSelectAll",
		PRINT: "globalPrint"
	},
	CONTROL: { DELETE: "controlDelete" },
	HYPERLINK: {
		DELETE: "hyperlinkDelete",
		CANCEL: "hyperlinkCancel",
		EDIT: "hyperlinkEdit"
	},
	IMAGE: {
		CHANGE: "imageChange",
		SAVE_AS: "imageSaveAs",
		TEXT_WRAP: "imageTextWrap",
		TEXT_WRAP_EMBED: "imageTextWrapEmbed",
		TEXT_WRAP_UP_DOWN: "imageTextWrapUpDown",
		TEXT_WRAP_SURROUND: "imageTextWrapSurround",
		TEXT_WRAP_FLOAT_TOP: "imageTextWrapFloatTop",
		TEXT_WRAP_FLOAT_BOTTOM: "imageTextWrapFloatBottom"
	},
	TABLE: {
		BORDER: "border",
		BORDER_ALL: "tableBorderAll",
		BORDER_EMPTY: "tableBorderEmpty",
		BORDER_DASH: "tableBorderDash",
		BORDER_EXTERNAL: "tableBorderExternal",
		BORDER_INTERNAL: "tableBorderInternal",
		BORDER_TD: "tableBorderTd",
		BORDER_TD_TOP: "tableBorderTdTop",
		BORDER_TD_RIGHT: "tableBorderTdRight",
		BORDER_TD_BOTTOM: "tableBorderTdBottom",
		BORDER_TD_LEFT: "tableBorderTdLeft",
		BORDER_TD_FORWARD: "tableBorderTdForward",
		BORDER_TD_BACK: "tableBorderTdBack",
		VERTICAL_ALIGN: "tableVerticalAlign",
		VERTICAL_ALIGN_TOP: "tableVerticalAlignTop",
		VERTICAL_ALIGN_MIDDLE: "tableVerticalAlignMiddle",
		VERTICAL_ALIGN_BOTTOM: "tableVerticalAlignBottom",
		INSERT_ROW_COL: "tableInsertRowCol",
		INSERT_TOP_ROW: "tableInsertTopRow",
		INSERT_BOTTOM_ROW: "tableInsertBottomRow",
		INSERT_LEFT_COL: "tableInsertLeftCol",
		INSERT_RIGHT_COL: "tableInsertRightCol",
		DELETE_ROW_COL: "tableDeleteRowCol",
		DELETE_ROW: "tableDeleteRow",
		DELETE_COL: "tableDeleteCol",
		DELETE_TABLE: "tableDeleteTable",
		MERGE_CELL: "tableMergeCell",
		CANCEL_MERGE_CELL: "tableCancelMergeCell",
		AUTO_FIT_TO_CONTENT: "tableAutoFitToContent",
		AUTO_FIT_TO_PAGE: "tableAutoFitToPage"
	}
}, { CONTROL: { DELETE: Bo } } = zo, Vo = [{
	key: Bo,
	i18nPath: "contextmenu.control.delete",
	when: (e) => !e.isReadonly && !e.editorHasSelection && !!e.startElement?.controlId && e.options.mode !== p.FORM,
	callback: (e) => {
		e.executeRemoveControl();
	}
}], { GLOBAL: { CUT: Ho, COPY: Uo, PASTE: Wo, SELECT_ALL: Go, PRINT: Ko } } = zo, qo = [
	{
		key: Ho,
		i18nPath: "contextmenu.global.cut",
		shortCut: `${xe ? "⌘" : "Ctrl"} + X`,
		when: (e) => !e.isReadonly,
		callback: (e) => {
			e.executeCut();
		}
	},
	{
		key: Uo,
		i18nPath: "contextmenu.global.copy",
		shortCut: `${xe ? "⌘" : "Ctrl"} + C`,
		when: (e) => e.editorHasSelection || e.isCrossRowCol,
		callback: (e) => {
			e.executeCopy();
		}
	},
	{
		key: Wo,
		i18nPath: "contextmenu.global.paste",
		shortCut: `${xe ? "⌘" : "Ctrl"} + V`,
		when: (e) => !e.isReadonly && e.editorTextFocus,
		callback: (e) => {
			e.executePaste();
		}
	},
	{
		key: Go,
		i18nPath: "contextmenu.global.selectAll",
		shortCut: `${xe ? "⌘" : "Ctrl"} + A`,
		when: (e) => e.editorTextFocus,
		callback: (e) => {
			e.executeSelectAll();
		}
	},
	{ isDivider: !0 },
	{
		key: Ko,
		i18nPath: "contextmenu.global.print",
		icon: "print",
		when: () => !0,
		callback: (e) => {
			e.executePrint();
		}
	}
], { HYPERLINK: { DELETE: Jo, CANCEL: Yo, EDIT: Xo } } = zo, Zo = [
	{
		key: Jo,
		i18nPath: "contextmenu.hyperlink.delete",
		when: (e) => !e.isReadonly && e.startElement?.type === H.HYPERLINK,
		callback: (e) => {
			e.executeDeleteHyperlink();
		}
	},
	{
		key: Yo,
		i18nPath: "contextmenu.hyperlink.cancel",
		when: (e) => !e.isReadonly && e.startElement?.type === H.HYPERLINK,
		callback: (e) => {
			e.executeCancelHyperlink();
		}
	},
	{
		key: Xo,
		i18nPath: "contextmenu.hyperlink.edit",
		when: (e) => !e.isReadonly && e.startElement?.type === H.HYPERLINK,
		callback: (e, t) => {
			let n = window.prompt(e.executeTranslate("contextmenu.hyperlink.edit"), t.startElement?.url);
			n && e.executeEditHyperlink(n);
		}
	}
], { IMAGE: { CHANGE: Qo, SAVE_AS: $o, TEXT_WRAP: es, TEXT_WRAP_EMBED: ts, TEXT_WRAP_UP_DOWN: ns, TEXT_WRAP_SURROUND: rs, TEXT_WRAP_FLOAT_TOP: is, TEXT_WRAP_FLOAT_BOTTOM: as } } = zo, os = [
	{
		key: Qo,
		i18nPath: "contextmenu.image.change",
		icon: "image-change",
		when: (e) => !e.isReadonly && !e.editorHasSelection && e.startElement?.type === H.IMAGE,
		callback: (e) => {
			let t = document.createElement("input");
			t.type = "file", t.accept = ".png, .jpg, .jpeg", t.onchange = () => {
				let n = t.files[0], r = new FileReader();
				r.readAsDataURL(n), r.onload = () => {
					let t = r.result;
					e.executeReplaceImageElement(t);
				};
			}, t.click();
		}
	},
	{
		key: $o,
		i18nPath: "contextmenu.image.saveAs",
		icon: "image",
		when: (e) => !e.editorHasSelection && e.startElement?.type === H.IMAGE,
		callback: (e) => {
			e.executeSaveAsImageElement();
		}
	},
	{
		key: es,
		i18nPath: "contextmenu.image.textWrap",
		when: (e) => !e.isReadonly && !e.editorHasSelection && e.startElement?.type === H.IMAGE,
		childMenus: [
			{
				key: ts,
				i18nPath: "contextmenu.image.textWrapType.embed",
				when: () => !0,
				callback: (e, t) => {
					e.executeChangeImageDisplay(t.startElement, r.BLOCK);
				}
			},
			{
				key: ns,
				i18nPath: "contextmenu.image.textWrapType.upDown",
				when: () => !0,
				callback: (e, t) => {
					e.executeChangeImageDisplay(t.startElement, r.INLINE);
				}
			},
			{
				key: rs,
				i18nPath: "contextmenu.image.textWrapType.surround",
				when: () => !0,
				callback: (e, t) => {
					e.executeChangeImageDisplay(t.startElement, r.SURROUND);
				}
			},
			{
				key: is,
				i18nPath: "contextmenu.image.textWrapType.floatTop",
				when: () => !0,
				callback: (e, t) => {
					e.executeChangeImageDisplay(t.startElement, r.FLOAT_TOP);
				}
			},
			{
				key: as,
				i18nPath: "contextmenu.image.textWrapType.floatBottom",
				when: () => !0,
				callback: (e, t) => {
					e.executeChangeImageDisplay(t.startElement, r.FLOAT_BOTTOM);
				}
			}
		]
	}
], { TABLE: { BORDER: ss, BORDER_ALL: cs, BORDER_EMPTY: ls, BORDER_DASH: us, BORDER_EXTERNAL: ds, BORDER_INTERNAL: fs, BORDER_TD: ps, BORDER_TD_TOP: ms, BORDER_TD_LEFT: hs, BORDER_TD_BOTTOM: gs, BORDER_TD_RIGHT: _s, BORDER_TD_BACK: vs, BORDER_TD_FORWARD: ys, VERTICAL_ALIGN: bs, VERTICAL_ALIGN_TOP: xs, VERTICAL_ALIGN_MIDDLE: Ss, VERTICAL_ALIGN_BOTTOM: Cs, INSERT_ROW_COL: ws, INSERT_TOP_ROW: Ts, INSERT_BOTTOM_ROW: Es, INSERT_LEFT_COL: Ds, INSERT_RIGHT_COL: Os, DELETE_ROW_COL: ks, DELETE_ROW: As, DELETE_COL: js, DELETE_TABLE: Ms, MERGE_CELL: Ns, CANCEL_MERGE_CELL: Ps, AUTO_FIT_TO_CONTENT: Fs, AUTO_FIT_TO_PAGE: Is } } = zo, Ls = [
	{ isDivider: !0 },
	{
		key: ss,
		i18nPath: "contextmenu.table.border",
		icon: "border-all",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		childMenus: [
			{
				key: cs,
				i18nPath: "contextmenu.table.borderAll",
				icon: "border-all",
				when: () => !0,
				callback: (e) => {
					e.executeTableBorderType(kt.ALL);
				}
			},
			{
				key: ls,
				i18nPath: "contextmenu.table.borderEmpty",
				icon: "border-empty",
				when: () => !0,
				callback: (e) => {
					e.executeTableBorderType(kt.EMPTY);
				}
			},
			{
				key: us,
				i18nPath: "contextmenu.table.borderDash",
				icon: "border-dash",
				when: () => !0,
				callback: (e) => {
					e.executeTableBorderType(kt.DASH);
				}
			},
			{
				key: ds,
				i18nPath: "contextmenu.table.borderExternal",
				icon: "border-external",
				when: () => !0,
				callback: (e) => {
					e.executeTableBorderType(kt.EXTERNAL);
				}
			},
			{
				key: fs,
				i18nPath: "contextmenu.table.borderInternal",
				icon: "border-internal",
				when: () => !0,
				callback: (e) => {
					e.executeTableBorderType(kt.INTERNAL);
				}
			},
			{
				key: ps,
				i18nPath: "contextmenu.table.borderTd",
				icon: "border-td",
				when: () => !0,
				childMenus: [
					{
						key: ms,
						i18nPath: "contextmenu.table.borderTdTop",
						icon: "border-td-top",
						when: () => !0,
						callback: (e) => {
							e.executeTableTdBorderType(At.TOP);
						}
					},
					{
						key: _s,
						i18nPath: "contextmenu.table.borderTdRight",
						icon: "border-td-right",
						when: () => !0,
						callback: (e) => {
							e.executeTableTdBorderType(At.RIGHT);
						}
					},
					{
						key: gs,
						i18nPath: "contextmenu.table.borderTdBottom",
						icon: "border-td-bottom",
						when: () => !0,
						callback: (e) => {
							e.executeTableTdBorderType(At.BOTTOM);
						}
					},
					{
						key: hs,
						i18nPath: "contextmenu.table.borderTdLeft",
						icon: "border-td-left",
						when: () => !0,
						callback: (e) => {
							e.executeTableTdBorderType(At.LEFT);
						}
					},
					{
						key: ys,
						i18nPath: "contextmenu.table.borderTdForward",
						icon: "border-td-forward",
						when: () => !0,
						callback: (e) => {
							e.executeTableTdSlashType(jt.FORWARD);
						}
					},
					{
						key: vs,
						i18nPath: "contextmenu.table.borderTdBack",
						icon: "border-td-back",
						when: () => !0,
						callback: (e) => {
							e.executeTableTdSlashType(jt.BACK);
						}
					}
				]
			}
		]
	},
	{
		key: bs,
		i18nPath: "contextmenu.table.verticalAlign",
		icon: "vertical-align",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		childMenus: [
			{
				key: xs,
				i18nPath: "contextmenu.table.verticalAlignTop",
				icon: "vertical-align-top",
				when: () => !0,
				callback: (e) => {
					e.executeTableTdVerticalAlign(Y.TOP);
				}
			},
			{
				key: Ss,
				i18nPath: "contextmenu.table.verticalAlignMiddle",
				icon: "vertical-align-middle",
				when: () => !0,
				callback: (e) => {
					e.executeTableTdVerticalAlign(Y.MIDDLE);
				}
			},
			{
				key: Cs,
				i18nPath: "contextmenu.table.verticalAlignBottom",
				icon: "vertical-align-bottom",
				when: () => !0,
				callback: (e) => {
					e.executeTableTdVerticalAlign(Y.BOTTOM);
				}
			}
		]
	},
	{
		key: ws,
		i18nPath: "contextmenu.table.insertRowCol",
		icon: "insert-row-col",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		childMenus: [
			{
				key: Ts,
				i18nPath: "contextmenu.table.insertTopRow",
				icon: "insert-top-row",
				when: () => !0,
				callback: (e) => {
					e.executeInsertTableTopRow();
				}
			},
			{
				key: Es,
				i18nPath: "contextmenu.table.insertBottomRow",
				icon: "insert-bottom-row",
				when: () => !0,
				callback: (e) => {
					e.executeInsertTableBottomRow();
				}
			},
			{
				key: Ds,
				i18nPath: "contextmenu.table.insertLeftCol",
				icon: "insert-left-col",
				when: () => !0,
				callback: (e) => {
					e.executeInsertTableLeftCol();
				}
			},
			{
				key: Os,
				i18nPath: "contextmenu.table.insertRightCol",
				icon: "insert-right-col",
				when: () => !0,
				callback: (e) => {
					e.executeInsertTableRightCol();
				}
			}
		]
	},
	{
		key: ks,
		i18nPath: "contextmenu.table.deleteRowCol",
		icon: "delete-row-col",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		childMenus: [
			{
				key: As,
				i18nPath: "contextmenu.table.deleteRow",
				icon: "delete-row",
				when: () => !0,
				callback: (e) => {
					e.executeDeleteTableRow();
				}
			},
			{
				key: js,
				i18nPath: "contextmenu.table.deleteCol",
				icon: "delete-col",
				when: () => !0,
				callback: (e) => {
					e.executeDeleteTableCol();
				}
			},
			{
				key: Ms,
				i18nPath: "contextmenu.table.deleteTable",
				icon: "delete-table",
				when: () => !0,
				callback: (e) => {
					e.executeDeleteTable();
				}
			}
		]
	},
	{
		key: Ns,
		i18nPath: "contextmenu.table.mergeCell",
		icon: "merge-cell",
		when: (e) => !e.isReadonly && e.isCrossRowCol && e.options.mode !== p.FORM,
		callback: (e) => {
			e.executeMergeTableCell();
		}
	},
	{
		key: Ps,
		i18nPath: "contextmenu.table.mergeCancelCell",
		icon: "merge-cancel-cell",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		callback: (e) => {
			e.executeCancelMergeTableCell();
		}
	},
	{
		key: Fs,
		i18nPath: "contextmenu.table.autoFitToContent",
		icon: "table-auto-fit-content",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		callback: (e) => {
			e.executeTableAutoFitToContent();
		}
	},
	{
		key: Is,
		i18nPath: "contextmenu.table.autoFitToPage",
		icon: "table-auto-fit-page",
		when: (e) => !e.isReadonly && e.isInTable && e.options.mode !== p.FORM,
		callback: (e) => {
			e.executeTableAutoFitToPage();
		}
	}
], Rs = class {
	options;
	draw;
	command;
	range;
	position;
	i18n;
	container;
	contextMenuList;
	contextMenuContainerList;
	contextMenuRelationShip;
	context;
	constructor(e, t) {
		this.options = e.getOptions(), this.draw = e, this.command = t, this.range = e.getRange(), this.position = e.getPosition(), this.i18n = e.getI18n(), this.container = e.getContainer(), this.context = null, this.contextMenuList = [
			...qo,
			...Ls,
			...os,
			...Vo,
			...Zo
		], this.contextMenuContainerList = [], this.contextMenuRelationShip = /* @__PURE__ */ new Map(), this._addEvent();
	}
	getContextMenuList() {
		return this.contextMenuList;
	}
	_addEvent() {
		this.container.addEventListener("contextmenu", this._proxyContextMenuEvent), document.addEventListener("mousedown", this._handleSideEffect);
	}
	removeEvent() {
		this.container.removeEventListener("contextmenu", this._proxyContextMenuEvent), document.removeEventListener("mousedown", this._handleSideEffect);
	}
	_filterMenuList(e) {
		let { contextMenuDisableKeys: t } = this.options, n = [];
		for (let r = 0; r < e.length; r++) {
			let i = e[r];
			i.disable || i.key && t.includes(i.key) || (i.isDivider || i.when?.(this.context)) && n.push(i);
		}
		return n;
	}
	_proxyContextMenuEvent = (e) => {
		this.context = this._getContext();
		let t = this._filterMenuList(this.contextMenuList);
		t.some((e) => !e.isDivider) && (this.dispose(), this._render({
			contextMenuList: t,
			left: e.x,
			top: e.y
		})), e.preventDefault();
	};
	_handleSideEffect = (e) => {
		this.contextMenuContainerList.length && (j(e?.composedPath()[0] || e.target, (e) => !!e && e.nodeType === 1 && e.getAttribute("editor-component") === d.CONTEXTMENU, !0) || this.dispose());
	};
	_getContext() {
		let e = this.draw.isReadonly(), { isCrossRowCol: t, startIndex: n, endIndex: r } = this.range.getRange(), i = !!(~n || ~r), a = i && n !== r, { isTable: o, trIndex: s, tdIndex: c, index: l } = this.position.getPositionContext(), u = null;
		if (o) {
			let e = this.draw.getOriginalElementList()[l] || null;
			e && (u = X([e], { extraPickAttrs: ["id"] })[0]);
		}
		let d = o && !!t, f = this.draw.getElementList();
		return {
			startElement: f[n] || null,
			endElement: f[r] || null,
			isReadonly: e,
			editorHasSelection: a,
			editorTextFocus: i,
			isCrossRowCol: d,
			zone: this.draw.getZone().getZone(),
			isInTable: o,
			trIndex: s ?? null,
			tdIndex: c ?? null,
			tableElement: u,
			options: this.options
		};
	}
	_createContextMenuContainer() {
		let e = document.createElement("div");
		return e.classList.add("ce-contextmenu-container"), e.setAttribute(_e, d.CONTEXTMENU), this.container.append(e), e;
	}
	_render(e) {
		let { contextMenuList: t, left: n, top: r, parentMenuContainer: i } = e, a = this._createContextMenuContainer(), o = document.createElement("div");
		o.classList.add("ce-contextmenu-content");
		let s = null;
		i && this.contextMenuRelationShip.set(i, a);
		for (let e = 0; e < t.length; e++) {
			let n = t[e];
			if (n.isDivider) {
				if (e !== 0 && e !== t.length - 1 && !t[e - 1]?.isDivider) {
					let e = document.createElement("div");
					e.classList.add("ce-contextmenu-divider"), o.append(e);
				}
			} else {
				let e = document.createElement("div");
				if (e.classList.add("ce-contextmenu-item"), n.childMenus) {
					let t = this._filterMenuList(n.childMenus);
					t.some((e) => !e.isDivider) && (e.classList.add("ce-contextmenu-sub-item"), e.onmouseenter = () => {
						this._setHoverStatus(e, !0), this._removeSubMenu(a);
						let n = e.getBoundingClientRect(), r = n.left + n.width, i = n.top;
						s = this._render({
							contextMenuList: t,
							left: r,
							top: i,
							parentMenuContainer: a
						});
					}, e.onmouseleave = (t) => {
						(!s || !s.contains(t.relatedTarget)) && this._setHoverStatus(e, !1);
					});
				} else e.onmouseenter = () => {
					this._setHoverStatus(e, !0), this._removeSubMenu(a);
				}, e.onmouseleave = () => {
					this._setHoverStatus(e, !1);
				}, e.onclick = () => {
					n.callback && this.context && n.callback(this.command, this.context), this.dispose();
				};
				let t = document.createElement("i");
				e.append(t), n.icon && t.classList.add(`ce-contextmenu-${n.icon}`);
				let r = document.createElement("span"), i = n.i18nPath ? this._formatName(this.i18n.t(n.i18nPath)) : this._formatName(n.name || "");
				if (r.append(document.createTextNode(i)), e.append(r), n.shortCut) {
					let t = document.createElement("span");
					t.classList.add("ce-shortcut"), t.append(document.createTextNode(n.shortCut)), e.append(t);
				}
				o.append(e);
			}
		}
		a.append(o), a.style.display = "block";
		let c = window.innerWidth, l = a.getBoundingClientRect(), u = l.width, d = n + u > c ? n - u : n;
		a.style.left = `${d}px`;
		let f = window.innerHeight, p = l.height, m = r + p > f ? r - p : r;
		return a.style.top = `${m}px`, this.contextMenuContainerList.push(a), a;
	}
	_removeSubMenu(e) {
		let t = this.contextMenuRelationShip.get(e);
		t && (this._removeSubMenu(t), t.remove(), this.contextMenuRelationShip.delete(e));
	}
	_setHoverStatus(e, t) {
		t ? (e.parentNode?.querySelectorAll("ce-contextmenu-item").forEach((e) => e.classList.remove("hover")), e.classList.add("hover")) : e.classList.remove("hover");
	}
	_formatName(e) {
		let t = Object.values(Ro), n = RegExp(`${t.join("|")}`), r = e;
		if (n.test(r)) {
			let e = new RegExp(Ro.SELECTED_TEXT, "g");
			if (e.test(r)) {
				let t = this.range.toString();
				r = r.replace(e, t);
			}
		}
		return r;
	}
	registerContextMenuList(e) {
		this.contextMenuList.push(...e);
	}
	dispose() {
		this.contextMenuContainerList.forEach((e) => e.remove()), this.contextMenuContainerList = [], this.contextMenuRelationShip.clear();
	}
}, zs = [
	{
		key: Z.X,
		ctrl: !0,
		shift: !0,
		callback: (e) => {
			e.executeStrikeout();
		}
	},
	{
		key: Z.LEFT_BRACKET,
		mod: !0,
		callback: (e) => {
			e.executeSizeAdd();
		}
	},
	{
		key: Z.RIGHT_BRACKET,
		mod: !0,
		callback: (e) => {
			e.executeSizeMinus();
		}
	},
	{
		key: Z.B,
		mod: !0,
		callback: (e) => {
			e.executeBold();
		}
	},
	{
		key: Z.I,
		mod: !0,
		callback: (e) => {
			e.executeItalic();
		}
	},
	{
		key: Z.U,
		mod: !0,
		callback: (e) => {
			e.executeUnderline();
		}
	},
	{
		key: xe ? Z.COMMA : Z.RIGHT_ANGLE_BRACKET,
		mod: !0,
		shift: !0,
		callback: (e) => {
			e.executeSuperscript();
		}
	},
	{
		key: xe ? Z.PERIOD : Z.LEFT_ANGLE_BRACKET,
		mod: !0,
		shift: !0,
		callback: (e) => {
			e.executeSubscript();
		}
	},
	{
		key: Z.L,
		mod: !0,
		callback: (e) => {
			e.executeRowFlex(u.LEFT);
		}
	},
	{
		key: Z.E,
		mod: !0,
		callback: (e) => {
			e.executeRowFlex(u.CENTER);
		}
	},
	{
		key: Z.R,
		mod: !0,
		callback: (e) => {
			e.executeRowFlex(u.RIGHT);
		}
	},
	{
		key: Z.J,
		mod: !0,
		callback: (e) => {
			e.executeRowFlex(u.ALIGNMENT);
		}
	},
	{
		key: Z.J,
		mod: !0,
		shift: !0,
		callback: (e) => {
			e.executeRowFlex(u.JUSTIFY);
		}
	}
], Bs = [
	{
		key: Z.ZERO,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(null);
		}
	},
	{
		key: Z.ONE,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(W.FIRST);
		}
	},
	{
		key: Z.TWO,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(W.SECOND);
		}
	},
	{
		key: Z.THREE,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(W.THIRD);
		}
	},
	{
		key: Z.FOUR,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(W.FOURTH);
		}
	},
	{
		key: Z.FIVE,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(W.FIFTH);
		}
	},
	{
		key: Z.SIX,
		alt: !0,
		ctrl: !0,
		callback: (e) => {
			e.executeTitle(W.SIXTH);
		}
	}
], Vs = [{
	key: Z.I,
	shift: !0,
	mod: !0,
	callback: (e) => {
		e.executeList(mt.UL, _t.DISC);
	}
}, {
	key: Z.U,
	shift: !0,
	mod: !0,
	callback: (e) => {
		e.executeList(mt.OL);
	}
}], Hs = class {
	command;
	globalShortcutList;
	agentShortcutList;
	constructor(e, t) {
		this.command = t, this.globalShortcutList = [], this.agentShortcutList = [], this._addShortcutList([
			...zs,
			...Bs,
			...Vs
		]), this._addEvent(), e.getCursor().getAgentDom().addEventListener("keydown", this._agentKeydown.bind(this));
	}
	_addEvent() {
		document.addEventListener("keydown", this._globalKeydown);
	}
	removeEvent() {
		document.removeEventListener("keydown", this._globalKeydown);
	}
	_addShortcutList(e) {
		for (let t = e.length - 1; t >= 0; t--) {
			let n = e[t];
			n.isGlobal ? this.globalShortcutList.unshift(n) : this.agentShortcutList.unshift(n);
		}
	}
	registerShortcutList(e) {
		this._addShortcutList(e);
	}
	_globalKeydown = (e) => {
		this.globalShortcutList.length && this._execute(e, this.globalShortcutList);
	};
	_agentKeydown(e) {
		this.agentShortcutList.length && this._execute(e, this.agentShortcutList);
	}
	_execute(e, t) {
		for (let n = 0; n < t.length; n++) {
			let r = t[n];
			if ((r.mod ? or(e) === !!r.mod : e.ctrlKey === !!r.ctrl && e.metaKey === !!r.meta) && e.shiftKey === !!r.shift && e.altKey === !!r.alt && e.key.toLowerCase() === r.key.toLowerCase()) {
				r.disable || (r?.callback?.(this.command), e.preventDefault());
				break;
			}
		}
	}
}, Us;
(function(e) {
	e.RECORDED = "recorded", e.SCRIPT = "script";
})(Us ||= {});
//#endregion
//#region src/editor/core/plugin/Plugin.ts
var Ws = class {
	editor;
	constructor(e) {
		this.editor = e;
	}
	use(e, t) {
		e(this.editor, t);
	}
}, Gs = class {
	macros = /* @__PURE__ */ new Map();
	recording = null;
	isPlaying = !1;
	command;
	constructor(e) {
		this.command = e;
	}
	isRecording() {
		return this.recording !== null;
	}
	startRecording() {
		this.recording === null && (this.isPlaying || (this.recording = [], this.command.setInterceptor((e, t) => this.logStep(e, t))));
	}
	stopRecording(e) {
		if (this.recording === null) return null;
		this.command.setInterceptor(void 0);
		let t = {
			id: M(),
			name: e,
			type: Us.RECORDED,
			steps: this.recording
		};
		return this.recording = null, this.macros.set(t.id, t), t;
	}
	cancelRecording() {
		this.recording !== null && (this.command.setInterceptor(void 0), this.recording = null);
	}
	async play(e, ...t) {
		if (this.recording !== null) return;
		let n = this.findMacro(e);
		if (n) {
			this.isPlaying = !0;
			try {
				if (n.type === Us.RECORDED) for (let e of n.steps) {
					let t = this.command[e.command];
					if (typeof t != "function") return;
					try {
						await t.apply(this.command, e.args);
					} catch {
						return;
					}
				}
				else await n.handler(...t);
			} finally {
				this.isPlaying = !1;
			}
		}
	}
	getMacros() {
		return Array.from(this.macros.values());
	}
	getMacro(e) {
		return this.findMacro(e);
	}
	removeMacro(e) {
		let t = this.findMacro(e);
		return t ? this.macros.delete(t.id) : !1;
	}
	exportMacros() {
		let e = this.getMacros().filter((e) => e.type === Us.RECORDED);
		return JSON.stringify(e);
	}
	importMacros(e, t) {
		let n;
		try {
			n = JSON.parse(e);
		} catch {
			return;
		}
		if (!Array.isArray(n)) return;
		let r = t?.overwrite ?? !1;
		for (let e of n) {
			if (!qs(e)) return;
			this.macros.has(e.id) && !r || this.macros.set(e.id, { ...e });
		}
	}
	register(e, t) {
		let n = {
			id: M(),
			name: e,
			type: Us.SCRIPT,
			handler: t
		};
		return this.macros.set(n.id, n), n;
	}
	unregister(e) {
		let t = this.findMacro(e);
		return t ? this.macros.delete(t.id) : !1;
	}
	findMacro(e) {
		if (this.macros.has(e)) return this.macros.get(e);
		for (let t of this.macros.values()) if (t.name === e) return t;
	}
	logStep(e, t) {
		if (this.recording === null) return;
		let n;
		try {
			n = JSON.parse(JSON.stringify(t));
		} catch {
			return;
		}
		this.recording.push({
			command: e,
			args: n
		});
	}
};
function Ks(e) {
	if (typeof e != "object" || !e) return !1;
	let t = e;
	return typeof t.command == "string" && Array.isArray(t.args);
}
function qs(e) {
	if (typeof e != "object" || !e) return !1;
	let t = e;
	return typeof t.id == "string" && typeof t.name == "string" && t.type === Us.RECORDED && Array.isArray(t.steps) && t.steps.every(Ks);
}
//#endregion
//#region src/editor/core/event/eventbus/EventBus.ts
var Js = class {
	eventHub;
	constructor() {
		this.eventHub = /* @__PURE__ */ new Map();
	}
	on(e, t) {
		if (!e || typeof t != "function") return;
		let n = this.eventHub.get(e) || /* @__PURE__ */ new Set();
		n.add(t), this.eventHub.set(e, n);
	}
	emit(e, t) {
		if (!e) return;
		let n = this.eventHub.get(e);
		if (n) {
			if (n.size === 1) return [...n][0](t);
			n.forEach((e) => e(t));
		}
	}
	off(e, t) {
		if (!e || typeof t != "function") return;
		let n = this.eventHub.get(e);
		n && n.delete(t);
	}
	isSubscribe(e) {
		let t = this.eventHub.get(e);
		return !!t && t.size > 0;
	}
	dangerouslyClearAll() {
		this.eventHub.clear();
	}
}, Ys = class {
	paste;
	pasteImage;
	copy;
	drop;
}, Xs = class {
	command;
	version;
	listener;
	eventBus;
	override;
	register;
	destroy;
	use;
	macro;
	constructor(t, n, r = {}) {
		let i = mn(r);
		n = k(n);
		let a = [], o = [], s = [], c = [];
		Array.isArray(n) ? o = n : (a = n.header || [], o = n.main, s = n.footer || [], c = n.graffiti || []), [
			a,
			o,
			s
		].forEach((e) => {
			yn(e, {
				editorOptions: i,
				isForceCompensation: !0
			});
		}), this.version = e, this.listener = new Io(), this.eventBus = new Js(), this.override = new Ys();
		let l = new oo(t, i, {
			header: a,
			main: o,
			footer: s,
			graffiti: c
		}, this.listener, this.eventBus, this.override);
		this.command = new so(new Fo(l)), this.macro = new Gs(this.command);
		let u = new Rs(l, this.command), d = new Hs(l, this.command);
		this.register = new Lo({
			contextMenu: u,
			shortcut: d,
			i18n: l.getI18n()
		}), this.destroy = () => {
			l.destroy(), d.removeEvent(), u.removeEvent(), this.eventBus.dangerouslyClearAll();
		};
		let f = new Ws(this);
		this.use = f.use.bind(f);
	}
};
//#endregion
export { eo as AreaMode, Nt as BackgroundRepeat, Mt as BackgroundSize, Et as BlockType, so as Command, K as ControlComponent, Dt as ControlIndentation, Ot as ControlState, G as ControlType, ve as EDITOR_CLIPBOARD, _e as EDITOR_COMPONENT, Xs as Editor, Xs as default, d as EditorComponent, p as EditorMode, m as EditorZone, H as ElementType, a as FlexDirection, zo as INTERNAL_CONTEXT_MENU_KEY, Xr as INTERNAL_SHORTCUT_KEY, r as ImageDisplay, Z as KeyMap, l as LETTER_CLASS, en as LineNumberType, _t as ListStyle, mt as ListType, i as LocationPosition, Us as MacroType, t as MaxHeightRatio, n as NumberType, h as PageMode, g as PaperDirection, v as RenderMode, u as RowFlex, kt as TableBorder, At as TdBorder, jt as TdSlash, ci as TextDecorationStyle, W as TitleLevel, Y as VerticalAlign, Zt as WatermarkLayer, Xt as WatermarkType, _ as WordBreak, Nn as createDomFromElementList, Fn as getElementListByHTML, In as getTextFromElementList, N as splitText };

//# sourceMappingURL=canvas-editor.js.map
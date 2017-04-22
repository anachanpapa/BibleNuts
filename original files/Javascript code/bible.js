var activeNo = "";
var getQAJS = "/PublicBibleStudyNotebook/default/getQA";
function selectVerse(no,qid){
    activeNo = $('#activeNo', parent.document).val();
    if(parseInt(activeNo, 10) == no) return;
    if (activeNo != ""){
        $('#vid_'+activeNo).removeClass('selected');     
    }    

    $('oneVerse').removeClass('selected'); 
    
    //alert(parseInt(activeNo, 10) == no);    
    //alert(no);
    
    activeNo = no;
    var book = $('#vid_'+activeNo).find('.bibleBook').text();
    var chapter = $('#vid_'+activeNo).find('.bibleChapter').text();
    var verse = $('#vid_'+activeNo).find('.bibleVerse').text();
    //alert(activeNo+":"+book+":"+chapter+":"+verse);
    
    $('#activeNo', parent.document).val(activeNo);
    $('#vid_'+activeNo).addClass('selected');

    $('#postBody', parent.document).find('.inputlimitation').attr("contenteditable", true);
    $('#postBody', parent.document).css("background","#fff");
    setLimitation2();
    $('#QsubmitButton', parent.document).attr("disabled", false);
    $('#QreferButton', parent.document).attr("disabled", false);      
    
    jQuery.post(getQAJS,      
        {activeNo:activeNo,book:book,chapter:chapter,verse:verse},
        function(data){
            //alert(data);
            var pair = data.split('&&&');
            var target = pair[0].split(':');
            var book = target[0];
            var chapter = target[1];
            var verse = target[2];
            var label = '<div id="selectBook">' + book + '</div><div id="selectChapter">' + chapter + '&nbsp;:&nbsp;</div>\
            <div id="selectVerse">' + verse + '</div>'; 
            $('#Selected', parent.document).html(label);
            
            if(pair[1]==""){
                $("#PastQA", parent.document).html("");
            }else{
                //alert(pair[1]);
                var set = pair[1].split('<>');
                //alert(set.length);
                var comments='<div id="comments">'; 
                for(var i=0; i<set.length; i++){
                    var _one = set[i];
                    var one = _one.split('|||');
                    var id = one[0]
                    var reply_num = one[1];
                    var arrow = '<div class="openQA" id="openQA_' + id + '"></div>';
                    if (reply_num != '0'){
                        arrow = '<div class="openQA" id="openQA_' + id + '">\
                        <div class="rightArrow" title="open" onclick="openReply(' + id + ',' + reply_num + ')"></div>&emsp;(+' + reply_num + ')</div>';
                    }                         
                    var on = one[2];
                    on = on.replace(/-/g,'/');
                    on = on.replace(/\s/,'&emsp;');
                    on = on.match(/^.{2}(.+).{10}$/)[1];
                    var by = one[3];
                    var body = one[4];
                    body = body.replace(/<p>|<\/p>/g,'');
                    body = body.replace(/<a href/,'<a target="_blank" href');
                    body = body.replace(/&lt;\/?div.*?&gt;/gi, "");
                    body = body.replace(/&lt;(\/?a.*?)&gt;/gi, "<$1>");
                    body = body.replace(/&amp;nbsp;/gi,'&nbsp;');
                    var cleanbody = body.replace(/<\/?[^>]+>/gi, "");
                    cleanbody = cleanbody.replace(/\'/g,'&rsquo;');
                    cleanbody = cleanbody.replace(/\"/g,'&rdquo;');
                    var line = 
                    '<div class="oneQ" id="oneQ_' + id + '">\
                        <div class="Qheader">';
                    line = line + arrow + 
                            '<div class="Qby">' + by + '</div>\
                            <div class="Qinfo"></div>\
                            <div class="Qon">' + on + '</div>\
                            <div class="Qreply"><img title="reply" class="RplImg"\
                            src="/PublicBibleStudyNotebook/static/images/reply.png" onclick="openReplyForm(\'' + id + '\',\'' + on + '\',\'' + by + '\',\'' + cleanbody + '\')"></div>\
                        </div>\
                        <div class="Qbody">' + body + '</div>\
                        <div class="QreplyForm" id="QreplyForm_' + id + '"></div>\
                        <div class="Qreplys" id="Qreplys_' + id + '"></div>\
                    </div>';
                    comments += line; 
                }
                comments += '</div>';
                //alert(comments);
                $("#PastQA", parent.document).html(comments);
            }
        }
    );
}

function setLimitation2(){
    $('.editable', parent.document).on('click', function(e){
        var ctl = e.target;
        if ($(ctl).hasClass('editable')){
            $(ctl).children('.inputArea').focus();
        }
    });
       
    $('.inputlimitation', parent.document).on('keydown', function(e) {
        if (e.which == 13) {
            return false;
        }
    });

    $('.inputlimitation', parent.document).on('focus', function(e) {
        $(this).parent("div").css("outline","solid 2px #B5B6FF");
    }).blur(function(){
        $(this).parent("div").css("outline","none");
    });
        
    $('.inputlimitation', parent.document).on('paste', function(e) {
        var ctl = $(this);
        var text = ctl.html();
        text = text.replace(/<(\/?[^>]+?)>/gi, "%%$1%%");
        ctl.html(text);
        setTimeout(function() {
            var new_text = ctl.html();
            //alert(new_text);
            new_text.replace(/\n/g, "");
            new_text = new_text.replace(/<\/?[^>]+?>/gi, "");
            new_text = new_text.replace(/%%(\/?[^%]+?)%%/gi, '<$1>');      
            ctl.html(new_text);
             
        }, 100);
    });
}
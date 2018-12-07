$(document).ready(function() {
    $('#aboutLink').click(function(){
        $('html, body').animate({scrollTop:$('#about').position().top}, 'slow');
        return false;
    });

    $('#regLink').click(function(){
        $('html, body').animate({scrollTop:$('#reg').position().top}, 'slow');
        return false;
    });

    $('#teamLink').click(function(){
        $('html, body').animate({scrollTop:$('#team').position().top}, 'slow');
        return false;
    });

    $('#homeLink').click(function(){
        $('html, body').animate({scrollTop:$('#home').position().top}, 'slow');
        return false;
    });

    $('#contactLink').click(function(){
        $('html, body').animate({scrollTop:$('#contact').position().top}, 'slow');
        return false;
    });
});


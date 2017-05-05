$(function () {
    //highlight My profile menu
    $("#myProfileMenu").css({'background':'darkred', 'color':'white'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'white', 'color':'black'});

    donorUrl=window.loggedInUser["@controls"].self.href
    bloodTypeUrl=window.loggedInUser["@controls"].bloodtype.href
    $.ajax({
        url: donorUrl,
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
    
       
        $("#fullNanme").text(data.firstname + " " + data.familyName)
        $("#birthday").text(" " + data.birthDate)
        $("#gender").text(" " + data.gender)
        $("#bloodTypeID").text(" " + data.bloodTypeId)
        $.get(bloodTypeUrl,function(data){
                
             $("#bloodTypeID").text(" " + data.name)
        });
        $("#phone").text(" " + data.telephone)
        $("#cityAddress").text(" " + data.city + ", " + data.address)
        $("#email").text(" " + data.email)
        
        
    });
});

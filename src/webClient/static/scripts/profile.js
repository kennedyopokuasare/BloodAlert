$(function () {
    //highlight My profile menu
    $("#myProfileMenu").css({'background':'darkred', 'color':'white'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'white', 'color':'black'});

    /**
     * here client code depicts a true hypermedia behavior, 
     * by using hypermdia links to find URLs
     */
    donorUrl=window.loggedInUser["@controls"].self.href
    bloodTypeUrl=window.loggedInUser["@controls"].bloodtype.href
    console.log(bloodTypeUrl);
    $.ajax({
        url: donorUrl,
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {    
        $("#fullNanme").text(data.firstname + " " + data.familyName)
        $("#birthday").text(" " + data.birthDate.slice(8,10) + "-" + data.birthDate.slice(5,7) + "-" +data.birthDate.slice(0,4))
        $("#gender").text(" " + data.gender)
        switch(data.bloodTypeId){
            case "btype-1":
                $("#bloodTypeID").text("O+");
                break;
            case "btype-2":
                $("#bloodTypeID").text("O-");
                break;
            case "btype-3":
                $("#bloodTypeID").text("A+");
                    break;
            case "btype-4":
                $("#bloodTypeID").text("A-");
                    break;
            case "btype-5":
                $("#bloodTypeID").text("B+");
                    break;
            case "btype-6":
                $("#bloodTypeID").text("B-");
                    break;
            case "btype-7":
                $("#bloodTypeID").text("AB+");
                    break;
            case "btype-8":
                $("#bloodTypeID").text("AB-");
        }
        $("#phone").text(" " + data.telephone)
        $("#cityAddress").text(" " + data.city + ", " + data.address)
        $("#email").text(" " + data.email)  
    });
});

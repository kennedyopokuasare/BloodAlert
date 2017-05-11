var bbankData;
var bbanksCount;
var bloodLevels;
var bbankIndex;

$(function () {
    //highlight Donate menu
    $("#myProfileMenu").css({'background':'white', 'color':'black'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'darkred', 'color':'white'});
    
    //get blood banks list
    $.ajax({
        url: "/bloodalert/bloodbanks",
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
        bbankData = data;
        bbanksCount = data.items.length;
        bloodLevels = new Array(bbanksCount); 
        for(i=0; i<bbanksCount; i++){bloodLevels[i] = new Array(8).fill(0);} //bloodLevels[0][0] shows the amount of btype-1 of the first blood bankand and so on.
        for (bbankIndex=0; bbankIndex < bbanksCount; bbankIndex++){
            getBloolLevels(bbankIndex);
            
        }
    });

});

function creatListHTML(){
    var map = new Array();
    var bbLocation = new Array();
    for (bbankIndex=0; bbankIndex < bbanksCount; bbankIndex++){

        $(
            '<li class="list-group-item">'+
                '<div class="row toggle" id="dropdown-bbank-' + bbankIndex + '" data-toggle="bbank-' +  bbankIndex + '">'+
                    '<div class="col-xs-10">'+
                        bbankData.items[bbankIndex].name +
                    '</div>'+
                    '<div class="col-xs-1"><i class="glyphicon glyphicon-chevron-down" style="right: -45px" ></i></div>'+
                '</div>'+
                '<div id="bbank-'+ bbankIndex + '">'+
                    '<hr></hr>'+
                    '<div class="container">'+
                        '<div class="fluid-row">'+
                            '<center>'+
                                '<p><b style="font-size:150% ; margin-bottom:10px">' + bbankData.items[bbankIndex].name + '</b></p>'+
                                '<div style="margin-bottom:5px"><i class="glyphicon glyphicon-map-marker"></i> ' + bbankData.items[bbankIndex].address +', ' + bbankData.items[bbankIndex].city + '</div>'+
                                '<div style="margin-bottom:30px">'+
                                    '<span><i class="glyphicon glyphicon-envelope"></i> ' + bbankData.items[bbankIndex].email +' &nbsp&nbsp&nbsp</span>'+
                                    '<span><i class="glyphicon glyphicon-earphone"></i> ' + bbankData.items[bbankIndex].telephone +'</span><br />'+
                                '</div>'+
                                '<div style="margin-bottom:20px; width:60%">'+
                                    '<div class="row">'+
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][0]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][0]+'%"></div>'+
                                            '<span id="bloodLabale-0" class="progress-type">O+</span>'+
                                        '</div>'+
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][1]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][1]+'%"></div>'+
                                            '<span id="bloodLabale-1" class="progress-type">O-</span>'+                                            
                                        '</div>'+  
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][2]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][2]+'%"></div>'+
                                            '<span id="bloodLabale-2" class="progress-type">A+</span>'+
                                        '</div>'+  
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][3]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][3]+'%"></div>'+
                                            '<span id="bloodLabale-3" class="progress-type">A-</span>'+
                                        '</div>'+  
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][4]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][4]+'%"></div>'+
                                            '<span id="bloodLabale-4" class="progress-type">B+</span>'+
                                        '</div>'+  
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][5]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][5]+'%"></div>'+
                                            '<span id="bloodLabale-5" class="progress-type">B-</span>'+
                                        '</div>'+  
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][6]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][6]+'%"></div>'+
                                            '<span id="bloodLabale-6" class="progress-type">AB+</span>'+
                                        '</div>'+  
                                        '<div class="progress">'+
                                            '<div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="'+bloodLevels[bbankIndex][7]+'" aria-valuemin="0" aria-valuemax="100" style="width: '+bloodLevels[bbankIndex][7]+'%"></div>'+
                                            '<span id="bloodLabale-7" class="progress-type">AB-</span>'+
                                        '</div>'+    
                                    '</div>'+
                                '</div>'+
                                '<div id="map-' +  bbankIndex + '" style="width:100%; height:100%; min-width:300px; min-height:300px; margin-top:10px; margin-bottom:10px">'+
                            '</center>'+
                        '</div>'+
                    '</div>'+
                '</div>'+
            '</li>'
        ).appendTo("#bbanksList");

        //locate blood banks on the maps
        bbLocation[bbankIndex] = new google.maps.LatLng(bbankData.items[bbankIndex].latitude, bbankData.items[bbankIndex].longitude);
        var mapOptions = {
            center: bbLocation,
            zoom: 15
        };
        var marker = new google.maps.Marker({
            position: bbLocation[bbankIndex],
            title: "Property Location"
        });
        map[bbankIndex] = new google.maps.Map(document.getElementById("map-"+bbankIndex), mapOptions);
        marker.setMap(map[bbankIndex]);
    }
        //make the list intractive
        $('[id^=bbank-]').hide();
        $('.toggle').click(function() {
            $input = $( this );
            $target = $('#'+$input.attr('data-toggle'));
            $target.slideToggle();
            for (bbankIndex=0; bbankIndex < bbanksCount; bbankIndex++){
                google.maps.event.trigger(map[bbankIndex], 'resize');
                map[bbankIndex].setCenter(bbLocation[bbankIndex]);
            }
        });
}

//getting the amount of all blood types for a blood bank
function getBloolLevels(bbIndex){
    $.ajax({
        url: "/bloodalert/bloodbanks/" + bbankData.items[bbIndex].bloodBankId + "/bloodlevels/" ,
        dataType: "json",
        beforeSend: function() {
            bbIndex = bbankIndex;
        },
    }).done(function (data, textStatus, jqXHR) {
        //calculate blood level for each type (1000 is considered as a full amount, and levels are in percentage)
        for (index=0; index < data.items.length; index++){
            switch(data.items[index].bloodTypeId){
                case "btype-1":
                    bloodLevels[bbIndex][0] = Math.round(data.items[index].amount / 10); // (amount / 1000) * 100
                    break;
                case "btype-2":
                    bloodLevels[bbIndex][1] = Math.round(data.items[index].amount / 10);
                    break;
                case "btype-3":
                    bloodLevels[bbIndex][2] = Math.round(data.items[index].amount / 10);
                    break;
                case "btype-4":
                    bloodLevels[bbIndex][3] = Math.round(data.items[index].amount / 10);
                    break;
                case "btype-5":
                    bloodLevels[bbIndex][4] = Math.round(data.items[index].amount / 10);
                    break;
                case "btype-6":
                    bloodLevels[bbIndex][5] = Math.round(data.items[index].amount / 10);
                    break;
                case "btype-7":
                    bloodLevels[bbIndex][6] = Math.round(data.items[index].amount / 10);
                    break;
                case "btype-8":
                    bloodLevels[bbIndex][7] = Math.round(data.items[index].amount / 10);
            }
        }
        if(bbIndex == (bbanksCount-1)){
            creatListHTML();
            // console.log(bloodLevels);
        }
    });
}

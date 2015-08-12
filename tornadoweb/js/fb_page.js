var submit_page = function submit_page(){
    var url = "/feedback5?";
    var form = document.getElementById("refresh-form");

    var selector = document.getElementById("tech_selector");
    var tech_id = selector.options[selector.selectedIndex].value;
    if (tech_id){
        var hv = document.createElement("p");
        hv.innerHTML = '<input type="hidden" name="ts" value="'+tech_id+'">';
        form.appendChild(hv);
        hv = undefined
    }
    var date_t = $("#date_to").val();
    console.log(date_t);
    if (date_t){
        hv = document.createElement("p");
        hv.innerHTML = '<input type="hidden" name="dt" value="'+date_t.replace(/\s/g, '')+'">';
        form.appendChild(hv);
        hv = undefined
    }
    var date_f = $("#date_from").val();
    if (date_f){
        hv = document.createElement("p");
        hv.innerHTML = '<input type="hidden" name="df" value="'+date_f.replace(/\s/g, '')+'">';
        form.appendChild(hv);
        hv = undefined
    }

    form.submit()
}
let isUrlValid = false;

function setupApp() {
    console.log('Ive loaded')
}

function test(el) {
    isUrlValid = false;
    input = el.value;
    if (input.includes("http://") || input.includes("https://")) {
        input = input.split(' ')
        url = input.find(string => {
            return string.startsWith('http://') || string.startsWith("https://")
        })
        if (url){   
            runImage(url, el, input)
            console.log("running Image checker with url: ", url)
        }
        console.log('url', url)
    }
}

function checkUrl2(el) {
    isUrlValid = false;
    url = el.value; 
    runImage(url, el, 2)
    console.log("running Image checker with url: ", url)
}

function testImage(url, timeoutT) {
    return new Promise(function (resolve, reject) {
        var timeout = timeoutT || 5000;
        var timer, img = new Image();
        img.onerror = img.onabort = function () {
            clearTimeout(timer);
            reject("error");
        };
        img.onload = function () {
            clearTimeout(timer);
            resolve("success");
        };
        timer = setTimeout(function () {
            // reset .src to invalid URL so it stops previous
            // loading, but doens't trigger new load
            img.src = "//!!!!/noexist.jpg";
            reject("timeout");
        }, timeout);
        img.src = url;
    });
}


function record(url, el, input, result) {
    if(input == 2) {
        img = el.parentElement.getElementsByTagName('img')[0]
        if(result == 'success'){
            el.setAttribute("name", "image_url")
            img.src = url
        } else {
            el.removeAttribute("name")
            img.src = ''
        }
    } else {
        preview = el.parentElement.getElementsByClassName('preview')[0]
        if (result == 'success') {
            preview.innerHTML = "<input name='image_url' class='col-12 imgURLForm mb-2' type='text' id='imgURLInput' onkeyup='checkUrl2(this)'/><br/><img class='col-6 previewImg rounded mb-3' src ='" + url + "' />";
            imgURLInput = document.getElementById('imgURLInput')
            imgURLInput.value = url
            
            input.pop(input.indexOf(url))
            preview.parentElement.getElementsByClassName('postInput')[0].value = input.join(' ')
        } else {
            preview.innerHTML = "<p>Invalid Link</p>"
        }
    }
}

function runImage(url, el, input) {
    testImage(url).then(record.bind(null, url, el, input), record.bind(null, url, el, input));
}

function replace1(el) {
    el.removeAttribute("class");
    el.setAttribute("class", "fas fa-bookmark followBtn")
}

function replace2(el) {
    el.removeAttribute("class");
    el.setAttribute("class", "far fa-bookmark followBtn")
}
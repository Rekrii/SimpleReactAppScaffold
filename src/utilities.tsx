import { Constants } from "./constants";
import Cookies from "universal-cookie";

// Redirecting cooking handling to universal-cookie
// https://github.com/reactivestack/cookies/tree/master/packages/universal-cookie
const cookies = new Cookies();

export function getCookieOrDefault(cname: string, defaultVal: any) {
  var c = getCookie(cname)
  if (c === "") {
    return defaultVal;
  }
  return c;
}

export function getCookie(cname: string) {
  var cookie = cookies.get(cname);
  if(cookie !== undefined) {
    return cookie;
  }

  return "";
}

export function setCookie(cname: string, cvalue: any, exdays: number) {
  cookies.set(cname, cvalue, { path: '/', maxAge:  exdays * 24 * 60 * 60});
}

export function getRandomColor() {
  // var letters = '0123456789ABCDEF';
  var letters = '23456789AB'; // Limiting to exclude near-black or near-white
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * (letters.length - 1))];
  }
  return color;
}

export function getDaysBetween(startDate: Date, endDate: Date) {
  const oneDay = 24 * 60 * 60 * 1000; // hours*minutes*seconds*milliseconds
  return Math.ceil((endDate.getTime() - startDate.getTime()) / oneDay);
}

// Gets today as a string formatted in 'yyyy-mm-dd' with jan=01
export function getTodayAsString() {
  var d = new Date();
  return d.getFullYear() + "-" + (d.getMonth() + 1).toString().padStart(2, '0') + "-" + d.getDate().toString().padStart(2, '0');
}

// Only push a string to the server, only get a string back
// App to convert to/from strings as required
export function pushDataToServer(col: string, data: string) {
  window.setTimeout(async () => {
    var name = getCookieOrDefault(Constants.cookieNameSessionName, "")
    var uuid = getCookieOrDefault(Constants.cookieNameStringSessionUuid, "")

    var myInit: RequestInit = {
      method: 'POST',
      body: JSON.stringify(
        {
          name: name,
          uuid: uuid,
          data_name: col,
          data_value: JSON.stringify(data),
          append: false,
          toggle: false
        }
      ),
      headers: new Headers(),
      mode: 'cors',
      credentials: 'include',
      cache: 'default'
    };

    var myRequest = new Request(Constants.baseUrl + "/api/set-data", myInit);
    var fetchResult = await fetch(myRequest);
    if (fetchResult.status === 200) {
      var result = await (fetchResult).text();
      result = JSON.parse(result);
      if (result) {
        console.log("Data saved to server.")
      } else {
        alert("Sending data to server failed. Please refresh the page.")
      }
    } else {
      alert("Sending data to server failed. Server may be offline. Please refresh the page.")
    }
  }, Constants.pushDataToServerTimeout);
}

export async function pullServerData(col: string) {
  var name = getCookieOrDefault(Constants.cookieNameSessionName, "")
  var uuid = getCookieOrDefault(Constants.cookieNameStringSessionUuid, "")
  console.log("uuid:", uuid);
  var myInit: RequestInit = {
    method: 'POST',
    body: JSON.stringify(
      {
        name: name,
        uuid: uuid,
        data_name: col
      }
    ),
    headers: new Headers(),
    mode: 'cors',
    credentials: 'include',
    cache: 'default'
  };

  var myRequest = new Request(Constants.baseUrl + "/api/get-data", myInit);

  var result = await (await fetch(myRequest)).text();
  result = JSON.parse(result)
  return result
}
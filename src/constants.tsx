
export class Constants {
  // Timeout in ms for how long to wait before pushing new data to server
  // multiple updates within this timeout will group into a single transmit
  static pushDataToServerTimeout = 1500;
  static appHomepage = process.env.REACT_APP_HOMEPAGE?.toString() || "No Homepage Set";
  static appSubdir = process.env.REACT_APP_BEPORT?.toString() || "";
  static baseUrl =  Constants.appHomepage + Constants.appSubdir;
  static cookieNameSessionName = 'app_session_name';
  static cookieNameStringSessionUuid = 'app_session_uuid';
}
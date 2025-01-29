Java.perform(function() {
    var targetClass = "com.digitral.network.ApiService";  // Replace with actual class name
    var clazz = Java.use(targetClass);

    var HeadersBuilder = Java.use("okhttp3.Headers$Builder");
    var MixUpValues = Java.use("com.digitral.common.MixUpValues");

    clazz.checkResponseHash.overload('java.lang.String', 'java.lang.String').implementation = function(str1, str2) {
        //console.log("[*] Bypassed checkResponseHash()");
        return true;
    }

    clazz.addOkHttpSignature.overload('java.lang.String', 'okhttp3.Headers$Builder').implementation = function(str, builder) {
        console.log("[*] Original str (REQBODY): " + str);

        /* Extract "X-IMI-TOKENID" header value
        var tokenId = builder.get("X-IMI-TOKENID");
        // console.log("[*] X-IMI-TOKENID: " + tokenId);

        if (tokenId !== null) {
            var mixUpInstance = MixUpValues.$new();
            var trimmedToken = mixUpInstance.getValues(tokenId);
            console.log("[*] Trimmed token value: " + trimmedToken);

            var encryptedValue = mixUpInstance.encryption("REQBODY=" + str + "&SALT=" + trimmedToken);
            console.log("[*] Encrypted value: " + encryptedValue);
        }*/

        // Call the original function with modified values
        this.addOkHttpSignature(str, builder);
    };

    /*clazz.addSecurityHash.overload('okhttp3.Headers$Builder').implementation = function(builder) {
        console.log("[*] Hooked addSecurityHash()");
        // Proceed with original function call
        this.addSecurityHash(builder);
        // Call builder.build() to obtain okhttp3.Headers instance
        var headers = builder.build();

        // Use headers.names().toArray() to get an array of header names
        var headerNames = headers.names().toArray();

        console.log("[*] Headers:");
        for (var i = 0; i < headerNames.length; i++) {
            var headerName = headerNames[i];
            var headerValue = headers.get(headerName);
            console.log("    " + headerName + ": " + headerValue);
        }
    };*/

        // Define the target class and methods
    var MixUpValues = Java.use("com.digitral.common.MixUpValues");

    // Hook into the 'encryption' method
    MixUpValues.encryption.overload('java.lang.String').implementation = function(string) {
        console.log("[*] Intercepted string before encryption: " + string);

        // You can modify the string here if necessary
        // var modifiedString = string + "_modified";

        // Call the original encryption method with the intercepted string
        var result = this.encryption(string);

        //console.log("[*] Encrypted value: " + result);

        // Return the encrypted result
        return result;
    };
});

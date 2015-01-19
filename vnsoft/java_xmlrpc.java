import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Vector;
import java.util.*;

import org.apache.xmlrpc.XmlRpcException;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

public class java_xmlrpc { 
	public static void main(String[] args) { 
		try{
			System.out.println("Hello World!"); 
			final String	url = "http://127.0.0.1:8069",
							db = "bj",
					        username = "admin",
					        password = "abcd";
		        
			final XmlRpcClient client = new XmlRpcClient();
			final XmlRpcClientConfigImpl common_config = new XmlRpcClientConfigImpl();
			common_config.setServerURL(
			    new URL(String.format("%s/xmlrpc/2/common", url)));
			int uid = (int)client.execute(
				    common_config, "authenticate", Arrays.asList(
				        db, username, password, Collections.emptyMap()));
			System.out.println(uid);
			
			final XmlRpcClient models = new XmlRpcClient() {{
			    setConfig(new XmlRpcClientConfigImpl() {{
			        setServerURL(new URL(String.format("%s/xmlrpc/2/object", url)));
			    }});
			}};
			models.execute("execute_kw", Arrays.asList(
			    db, uid, password,
			    "res.users", "set_pwd",
			    Arrays.asList(1,
			    "admin",
			    "123456")
			    //new HashMap() {{ put("id", 1);put("name","admin");put("value","abcd");put("args","");put("context",Collections.emptyMap()); }}
			));
			
			}
		catch(Exception e){
			e.printStackTrace();
		}
    } 
}
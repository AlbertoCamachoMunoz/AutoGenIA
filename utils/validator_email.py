# from application.utils.validators import is_valid_email

# def validate_email_request(request: EmailAgentRequest) -> None:
#     if not is_valid_email(request.from_email):
#         raise ValueError("Remitente no es un email válido.")
#     if request.cc:
#         for mail in request.cc:
#             if not is_valid_email(mail):
#                 raise ValueError(f"Email en CC no válido: {mail}")
#     if request.cco:
#         for mail in request.cco:
#             if not is_valid_email(mail):
#                 raise ValueError(f"Email en CCO no válido: {mail}")


# using System;
# using System.Collections.Generic;
# using System.Linq;
# using System.Text;
# using System.Text.RegularExpressions;
# using System.Threading.Tasks;

# namespace ERK.Interddi.Cmd.Tools
# {
# 	public static class MailHelper
# 	{
# 		public static bool IsValidEmail(string email)
# 		{
# 			if (string.IsNullOrWhiteSpace(email))
# 				return false;

# 			var pattern = @"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$";
# 			return Regex.IsMatch(email, pattern);
# 		}
# 	}
# }
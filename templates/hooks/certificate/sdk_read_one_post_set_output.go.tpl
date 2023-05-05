	if resp.Certificate.DomainValidationOptions != nil {
		statusDomainValidation := []*svcapitypes.DomainValidation{}
		for _, responseOption := range resp.Certificate.DomainValidationOptions {
			statusOption := &svcapitypes.DomainValidation{}
			if responseOption.DomainName != nil {
				statusOption.DomainName = responseOption.DomainName
			}
			if responseOption.ValidationDomain != nil {
				statusOption.ValidationDomain = responseOption.ValidationDomain
			}
            if responseOption.ValidationEmails != nil {
                statusOption.ValidationEmails = responseOption.ValidationEmails
            }
            if responseOption.ValidationMethod != nil {
                statusOption.ValidationMethod = responseOption.ValidationMethod
            }
            if responseOption.ValidationStatus != nil {
                statusOption.ValidationStatus = responseOption.ValidationStatus
            }
            if responseOption.ResourceRecord != nil {
                statusRecord := &svcapitypes.ResourceRecord{}

                if responseOption.ResourceRecord.Name != nil {
                    statusRecord.Name = responseOption.ResourceRecord.Name
                }

                if responseOption.ResourceRecord.Type != nil {
                    statusRecord.Type = responseOption.ResourceRecord.Type
                }

                if responseOption.ResourceRecord.Value != nil {
                    statusRecord.Value = responseOption.ResourceRecord.Value
                }

                statusOption.ResourceRecord = statusRecord
            }
			statusDomainValidation = append(statusDomainValidation, statusOption)
		}
		ko.Status.CertificateDomainValidationOptions = statusDomainValidation

    }

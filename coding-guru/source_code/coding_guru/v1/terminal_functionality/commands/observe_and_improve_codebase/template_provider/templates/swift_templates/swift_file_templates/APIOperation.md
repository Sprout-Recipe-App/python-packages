import APITime

// MARK: - Request Schema
///
///

public struct <<<CreatedPathStem>>>RequestSchema: HTTPRequestSchema, HTTPRequestHeaders, HTTPRequestQueryItems, HTTPRequestBody {
    // MARK: - Headers
    ///
    ///

    public let headers: [String: String]

    // MARK: - Query Items
    ///
    ///

    public let queryItems: [URLQueryItem]

    // MARK: - Body
    ///
    ///

    public let body: Body

    public struct Body: Encodable {
        let exampleBodyProperty: String
    }

    // MARK: - Initializers
    ///
    ///

    init(headers: [String: String], queryItems: [URLQueryItem], body: Body) {
        self.headers = headers
        self.queryItems = queryItems
        self.body = body
    }
}

// MARK: - Response Schema
//
//

public struct <<<CreatedPathStem>>>ResponseSchema: Decodable {
    let success: Bool
}

// MARK: - <<<CreatedPathStem>>>
///
///

public struct <<<CreatedPathStem>>>: APIOperation {
    // Type Aliases
    public typealias RequestSchema = <<<CreatedPathStem>>>RequestSchema
    public typealias ResponseSchema = <<<CreatedPathStem>>>ResponseSchema

    // MARK: - Properties
    ///
    ///

    // Endpoint Configuration Group
    public let apiConfigurationKey: String = APIConstants.backendConfigurationKey
    public let method: HTTPEndpoint.HTTPMethod
    public let path: String = "/<<<created-path-stem>>>"

    // Serialization Group
    public let requestDataEncoder = StandardJSONCoder.encoder
    public let responseDataDecoder = StandardJSONCoder.decoder

    // Request Data Group
    public let requestData: RequestSchema
}